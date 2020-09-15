from unittest import TestCase, main

from expects import expect, equal
from twin_sister import open_dependency_context

from questions_three.module_cfg.module_cfg import ModuleCfg


class TestValueAccess(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True)

    def tearDown(self):
        self.context.close()

    def test_as_index(self):
        key = "shazam"
        value = "shuzbut"
        sut = ModuleCfg(defaults={key: value})
        expect(sut[key]).to(equal(value))

    def test_as_index_case_insensitive(self):
        value = "shuzbut"
        sut = ModuleCfg(defaults={"shazaM": value})
        expect(sut["ShAzAm"]).to(equal(value))

    def test_as_attribute(self):
        key = "shazam"
        value = "shuzbut"
        sut = ModuleCfg(defaults={key: value})
        expect(getattr(sut, key)).to(equal(value))

    def test_as_attribute_case_insensitive(self):
        value = "shuzbut"
        sut = ModuleCfg(defaults={"shazaM": value})
        expect(getattr(sut, "ShAzAm")).to(equal(value))


if "__main__" == __name__:
    main()
