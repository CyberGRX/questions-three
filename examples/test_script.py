from questions_three.scaffolds.test_script import \
    precondition, skip, test, test_suite


with test_suite('ExampleSuite'):

    with test('A passing test'):
        assert True, 'That was easy'

    with test('A failing test'):
        assert False, 'Failing is easy too'

    with test('An errant test'):
        raise RuntimeError('Intentional error')

    with test('A skipped test'):
        skip("Let's not run this test.  It's rather silly.")

    with test('A test that skips because its precondition is not met'):
        precondition(False)

    with test('A test that runs because its precondition is met'):
        precondition(True)
