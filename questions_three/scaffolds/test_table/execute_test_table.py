from copy import deepcopy
from datetime import datetime
from functools import partial
from inspect import signature
from random import shuffle

from twin_sister import dependency

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.exceptions import TestSkipped

RESERVED_HEADERS = {'expect_exception', 'sample_size', 'test_name'}


def _extract_headers(table):
    return [header.replace(' ', '_') for header in table[0]]


def _validate_headers(*, func, headers):
    custom_headers = set(headers) - RESERVED_HEADERS
    keyword_args = set(signature(func).parameters.keys())
    if keyword_args != custom_headers:
        raise TypeError(
            f'Table headers {headers} do not match {func.__name__} '
            f'keyword args {keyword_args}')


def _extract_test_name(*, func, row):
    return row['reserved'].get(
        'test_name', f'{func.__name__} with {row["kwargs"]}')


def _validate_expect_exception(exception, row_number):
    if exception and not issubclass(exception, Exception):
        raise TypeError(
            f'Invalid exception type ({type(exception)}) '
            f'at row {row_number}')


def _validate_sample_size(size, row_number):
    try:
        if int(size) != size:
            raise ValueError()
    except ValueError as e:
        raise TypeError(
            f'Sample size "{size}" at row {row_number} is a {type(size)}. '
            'It must be an integer.') from e
    if size < 0:
        raise TypeError(f'Sample size at row {row_number} must be positive')


def _validate_test_name(name, existing_names, row_number):
    if name in existing_names:
        raise TypeError(
            f'Row {row_number} duplicates test_name {name}')


def _validate_table(rows):
    test_names = []
    row_number = 0
    for row in rows:
        reserved = row['reserved']
        _validate_expect_exception(
            reserved['expect_exception'], row_number=row_number)
        _validate_sample_size(reserved['sample_size'], row_number=row_number)
        test_name = reserved['test_name']
        _validate_test_name(
            test_name, existing_names=test_names,
            row_number=row_number)
        test_names.append(test_name)
        row_number += 1


def _expand_table(original):
    expanded = []
    for row in original:
        test_name = row['reserved']['test_name']
        sample_size = row['reserved']['sample_size']
        for n in range(sample_size):
            twin = deepcopy(row)
            if sample_size > 1:
                twin['reserved']['test_name'] = f'{test_name} sample {n+1}'
            expanded.append(twin)
    return expanded


def _parse_table(*, func, table):
    headers = _extract_headers(table)
    custom_headers = set(headers) - RESERVED_HEADERS
    reserved_headers = set(headers) - custom_headers
    naive_rows = [dict(zip(headers, row)) for row in table[1:]]
    rows = [
        {
            'reserved': {header: row[header] for header in reserved_headers},
            'kwargs': {header: row[header] for header in custom_headers}
        } for row in naive_rows]
    for row in rows:
        reserved = row['reserved']
        reserved['expect_exception'] = reserved.get('expect_exception', None)
        reserved['sample_size'] = reserved.get('sample_size', 1)
        reserved['test_name'] = _extract_test_name(func=func, row=row)
    _validate_table(rows)
    return _expand_table(rows)


def _call_expecting_exception(*, func, exception):
    try:
        func()
        if exception:
            assert False, f'Expected {exception.__name__} was not raised'
    except Exception as e:
        if not (exception and isinstance(e, exception)):
            raise


def _execute_test(*, func, row, suite_name):
    test_name = row['reserved']['test_name']
    event_kwargs = {
        'test_name': test_name,
        'suite_name': suite_name}
    EventBroker.publish(event=TestEvent.test_started, **event_kwargs)
    try:
        start_time = datetime.now()
        _call_expecting_exception(
            func=partial(func, **row['kwargs']),
            exception=row['reserved']['expect_exception'])
        end_time = datetime.now()
        EventBroker.publish(
            event=TestEvent.sample_measured, sample_parameters=row['kwargs'],
            sample_execution_seconds=(end_time - start_time).total_seconds(),
            **event_kwargs)
    except AssertionError as e:
        EventBroker.publish(
            event=TestEvent.test_failed, exception=e, **event_kwargs)
    except TestSkipped as e:
        EventBroker.publish(
            event=TestEvent.test_skipped, exception=e, **event_kwargs)
    except Exception as e:
        EventBroker.publish(
            event=TestEvent.test_erred, exception=e, **event_kwargs)
    EventBroker.publish(
        event=TestEvent.test_ended, **event_kwargs)


def execute_test_table(
        *, func, table, suite_name=None, randomize_order=False):
    if suite_name is None:
        suite_name = func.__name__
    headers = _extract_headers(table)
    _validate_headers(func=func, headers=headers)
    EventBroker.publish(event=TestEvent.suite_started, suite_name=suite_name)
    rows = _parse_table(func=func, table=table)
    if randomize_order:
        dependency(shuffle)(rows)
    for row in rows:
        _execute_test(func=func, row=row, suite_name=suite_name)
    EventBroker.publish(event=TestEvent.suite_ended, suite_name=suite_name)
