from questions_three.scaffolds.test_table import execute_test_table

TABLE = (
    ('operation', 'sample size'),
    ('1 + 1', 30),
    ('1 * 1', 60),
    ('1 / 1', 42))


def calculate(operation):
    exec(operation)


execute_test_table(
    suite_name='MeasureOperatorPerformance',
    table=TABLE, func=calculate, randomize_order=True)
