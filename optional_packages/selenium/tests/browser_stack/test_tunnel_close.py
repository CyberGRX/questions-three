import os
from subprocess import Popen
import tempfile
import time
from unittest import TestCase, main
from zipfile import ZipFile

from expects import expect, contain, have_length
from questions_three.http_client import HttpClient
from twin_sister.fakes import EndlessFake, MasterSpy
from twin_sister import open_dependency_context

from questions_three_selenium.browser_stack_tunnel import BrowserStackTunnel


def zip_archive(uncompressed, member_name):
    _, tmp_uncompressed = tempfile.mkstemp()
    _, tmp_compressed = tempfile.mkstemp()
    try:
        with open(tmp_uncompressed, "wb") as f:
            f.write(uncompressed)
        z = ZipFile(tmp_compressed, mode="a")
        z.write(tmp_uncompressed, member_name)
        z.close()
        with open(tmp_compressed, "rb") as f:
            return f.read()
    finally:
        os.remove(tmp_uncompressed)
        os.remove(tmp_compressed)


class FakeResponse:
    content = zip_archive(b"bbb", "BrowserStackLocal")
    status_code = 200


class HttpStub:
    def __call__(self, *args, **kwargs):
        return FakeResponse()

    def __getattr__(self, name):
        return self


class PopenStub(EndlessFake):
    returncode = None


class TestClose(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.context.set_env(BROWSERSTACK_ACCESS_KEY="fake")
        # Prevent real network activity
        self.context.inject_as_class(HttpClient, HttpStub())
        self.context.set_env(BROWSER_ACCESS_KEY="spam")
        self.popen_spy = MasterSpy(PopenStub())
        self.context.inject_as_class(Popen, self.popen_spy)
        # Thwart actual sleeping
        self.context.inject(time.sleep, lambda n: None)
        self.tunnel = BrowserStackTunnel()

    def tearDown(self):
        self.context.close()

    def test_kills_with_sigterm(self):
        self.tunnel.close()
        expect(self.popen_spy.attribute_spies.keys()).to(contain("terminate"))
        spy = self.popen_spy.attribute_spies["terminate"]
        expect(spy.call_history).to(have_length(1))


if "__main__" == __name__:
    main()
