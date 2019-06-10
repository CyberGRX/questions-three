from functools import partial
from unittest import TestCase, main

from expects import expect, equal
from questions_three.exceptions import InvalidConfiguration
from twin_sister.expects_matchers import complain
from twin_sister import open_dependency_context

from questions_three.module_cfg.module_cfg import ModuleCfg


UNSET = object()


class TestEnvVars(TestCase):

    def setUp(self):
        self.context = open_dependency_context(supply_env=True)

    def tearDown(self):
        self.context.close()

    def test_overrides_default_exact_case(self):
        key = 'something'
        default = 'default value'
        override = 'overridden value'
        cfg = ModuleCfg(defaults={key: default})
        self.context.os.environ[key] = override
        expect(cfg[key]).to(equal(override))

    def test_overrides_default_case_insensitive(self):
        default = 'default value'
        override = 'overridden value'
        cfg = ModuleCfg(defaults={'thing': default})
        self.context.os.environ['tHiNg'] = override
        expect(cfg['thing']).to(equal(override))

    def test_complains_about_ambiguous_environment(self):
        cfg = ModuleCfg(defaults={'thing': 'a'})
        self.context.os.environ['thing'] = 'b'
        self.context.os.environ['THING'] = 'c'
        expect(partial(getattr, cfg, 'thing')).to(
            complain(InvalidConfiguration))

    def expect_invalid(self, *, default, override):
        key = 'thing'
        defaults = {} if default is UNSET else {key: default}
        if override is not UNSET:
            self.context.os.environ[key] = override
        cfg = ModuleCfg(defaults=defaults)
        expect(partial(getattr, cfg, key)).to(complain(InvalidConfiguration))

    def expect_valid(self, *, default, override, expected):
        key = 'thing'
        self.context.os.environ[key] = str(override)
        cfg = ModuleCfg(defaults={key: default})
        expect(cfg[key]).to(equal(expected))

    def test_cannot_override_unconfigured_value(self):
        self.expect_invalid(default=UNSET, override='something')

    def test_cannot_override_int_with_non_numeric(self):
        self.expect_invalid(default=2, override='not-a-number')

    def test_cannot_override_int_with_bool(self):
        self.expect_invalid(default=2, override='true')

    def test_can_override_int_with_float(self):
        self.expect_valid(default=1, override=1.2, expected=1.2)

    def test_cannot_override_int_with_empty_str(self):
        self.expect_invalid(default=2, override='')

    def test_cannot_override_float_with_non_numeric(self):
        self.expect_invalid(default=2.2, override='rubbage')

    def test_cannot_override_float_with_empty_str(self):
        self.expect_invalid(default=2.2, override='')

    def test_cannot_override_float_with_bool(self):
        self.expect_invalid(default=2.2, override='true')

    def test_can_override_float_with_int(self):
        self.expect_valid(default=2.2, override=7, expected=7)

    def test_can_override_float_with_scientific_notation_no_sign(self):
        self.expect_valid(default=0, override='6.02e23', expected=6.02e+23)

    def test_can_override_float_with_scientific_notation_plus(self):
        self.expect_valid(default=42.0, override='6.02e+23', expected=6.02e+23)

    def test_can_override_float_with_scientific_notation_minus(self):
        self.expect_valid(default=42.0, override='6.02e-23', expected=6.02e-23)

    def test_scientific_notation_is_case_insensitive(self):
        self.expect_valid(default=42.0, override='6.02E-23', expected=6.02e-23)

    def test_cannot_override_bool_with_arbitrary_string(self):
        self.expect_invalid(default=True, override='The Spinach Imposition')

    def test_cannot_override_bool_with_number_above_one(self):
        self.expect_invalid(default=False, override=2)

    def test_cannot_override_bool_with_empty_str(self):
        self.expect_invalid(default=True, override='')

    def test_bool_true_is_true_case_insensitive(self):
        self.expect_valid(default=False, override='tRuE', expected=True)

    def test_bool_false_is_false_case_insensitive(self):
        self.expect_valid(default=True, override='fAlsE', expected=False)

    def test_bool_y_is_true(self):
        self.expect_valid(default=False, override='y', expected=True)

    def test_bool_Y_is_true(self):
        self.expect_valid(default=False, override='Y', expected=True)

    def test_bool_yes_is_true_case_insensitive(self):
        self.expect_valid(default=False, override='yEs', expected=True)

    def test_bool_N_is_false(self):
        self.expect_valid(default=False, override='N', expected=False)

    def test_bool_n_is_false(self):
        self.expect_valid(default=True, override='n', expected=False)

    def test_bool_0_is_false(self):
        self.expect_valid(default=True, override='0', expected=False)

    def test_bool_no_is_false_case_insensitive(self):
        self.expect_valid(default=True, override='no', expected=False)

    def test_bool_1_is_true(self):
        self.expect_valid(default=False, override='1', expected=True)

    def test_returns_int_as_str_if_default_is_str(self):
        self.expect_valid(default='spams', override='42', expected='42')

    def returns_float_as_str_if_default_is_str(self):
        self.expect_valid(default='spams', override='42.7', expected='42.7')

    def test_returns_bool_as_str_if_default_is_str(self):
        self.expect_valid(default='spasms', override='True', expected='True')

    def test_returns_numeric_bool_as_float_if_default_is_float(self):
        self.expect_valid(default=72.7, override='1', expected=1.0)


if '__main__' == __name__:
    main()
