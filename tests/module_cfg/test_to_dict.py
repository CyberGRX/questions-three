from unittest import TestCase, main

from expects import expect, contain, equal
from twin_sister import open_dependency_context

from questions_three.module_cfg.module_cfg import ModuleCfg


class TestToDict(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True)

    def tearDown(self):
        self.context.close()

    def test_contains_defaults(self):
        defaults = {"spams": 1, "eggs": 42, "sausage": None}
        sut = ModuleCfg(defaults=defaults)
        expect(sut.to_dict()).to(equal(defaults))

    def test_contains_env_overrides(self):
        overrides = {"spams": 4, "eggs": 13, "sausage": "biggles"}
        self.context.set_env(**overrides)
        sut = ModuleCfg(defaults={"spams": 0, "eggs": 0, "sausage": None})
        expect(sut.to_dict()).to(equal(overrides))

    def test_does_not_contain_undeclared_env_var(self):
        unexpected = "unexpected"
        self.context.set_env(**{unexpected: "something"})
        sut = ModuleCfg(defaults={})
        expect(sut.to_dict().keys()).not_to(contain(unexpected))

    def test_env_overrides_default(self):
        key = "penguin"
        override = "from_env"
        self.context.set_env(**{key: override})
        sut = ModuleCfg(defaults={key: "default"})
        expect(sut.to_dict()[key]).to(equal(override))


if "__main__" == __name__:
    main()
