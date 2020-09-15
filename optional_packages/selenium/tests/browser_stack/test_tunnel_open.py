import errno
import logging
import os
import re
import subprocess
from subprocess import Popen
import tempfile
import time
from unittest import TestCase, main
from zipfile import ZipFile

from expects import expect, equal
from questions_three.exceptions import InvalidConfiguration
from questions_three.http_client import HttpClient
from questions_three.vanilla import func_that_raises
from twin_sister import dependency, open_dependency_context
from twin_sister.expects_matchers import contain_key_with_value, raise_ex
from twin_sister.fakes import EndlessFake, MasterSpy

from questions_three_selenium.browser_stack_tunnel import BrowserStackTunnel
from questions_three_selenium.exceptions import BrowserStackTunnelClosed


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


class FakeHttpClient:
    def __init__(self):
        self.responses = {}

    def get(self, url):
        if url in self.responses.keys():
            return self.responses[url]
        raise RuntimeError("Unexpected request: %s" % url)


class FakeHttpResponse:
    def __init__(self, content, status_code=200):
        self.content = content
        self.headers = {}
        self.status_code = status_code


class FakePopen:
    def __init__(self):
        self.pid = 42
        self.returncode = None

    def __call__(self, *args, **kwargs):
        return self


class TestFirstOpen(TestCase):
    def setUp(self):
        self.context = open_dependency_context(supply_env=True, supply_fs=True)
        self.fake_http = FakeHttpClient()
        self.context.inject_as_class(HttpClient, self.fake_http)
        self.fake_popen = FakePopen()
        self.popen_spy = MasterSpy(self.fake_popen)
        self.context.inject(Popen, self.popen_spy)
        self.context.inject(logging, EndlessFake())
        # Thwart actual sleeping
        self.context.inject(time.sleep, lambda n: None)
        self.binary_zip_url = "https://where-we-expect.the/binary.zip"
        local_binary = "/where/we/put/the/binary"
        self.local_binary_path, self.local_binary_filename = os.path.split(local_binary)
        self.context.set_env(
            BROWSERSTACK_ACCESS_KEY="whatever",
            BROWSERSTACK_LOCAL_BINARY_ZIP_URL=self.binary_zip_url,
            BROWSERSTACK_LOCAL_BINARY=local_binary,
        )

    def tearDown(self):
        self.context.close()

    def join_path(self, *args):
        return self.context.os.path.join(*args)

    def create_fake_archive(self, content=b"bbbbb"):
        self.fake_http.responses[self.binary_zip_url] = FakeHttpResponse(
            content=zip_archive(uncompressed=content, member_name=self.local_binary_filename)
        )

    def test_stores_unzipped_binary_from_nexus(self):
        expected = b"spamspamspam243rwedf24r\x42spamandspam"
        self.create_fake_archive(content=expected)
        BrowserStackTunnel()
        full_path = self.join_path(self.local_binary_path, self.local_binary_filename)
        fopen = dependency(open)
        with fopen(full_path, "rb") as f:
            expect(f.read()).to(equal(expected))

    def attach_spy(self, target):
        current = dependency(target)
        spy = MasterSpy(current)
        self.context.inject(target, spy)
        return spy

    def test_writes_binary_in_binary_mode(self):
        full_path = self.join_path(self.local_binary_path, self.local_binary_filename)
        self.create_fake_archive()
        spy = self.attach_spy(open)
        BrowserStackTunnel()
        for args, kwargs in spy.call_history:
            if args[0] == full_path:
                expect(args[1]).to(equal("wb"))
                return
        raise RuntimeError("Failed to locate the open command")

    def test_sets_executable_bits(self):
        self.create_fake_archive()
        spy = MasterSpy(self.context.os.chmod)
        self.context.os.chmod = spy
        BrowserStackTunnel()
        assert spy.call_history, "chmod was not called"
        args, kwargs = spy.call_history[-1]
        expect(args).to(equal((self.join_path(self.local_binary_path, self.local_binary_filename), 0o775)))

    def test_creates_local_binary_path(self):
        self.create_fake_archive()
        spy = MasterSpy(self.context.os.makedirs)
        self.context.os.makedirs = spy
        BrowserStackTunnel()
        assert spy.call_history, "makedirs was not called"
        args, kwargs = spy.call_history[-1]
        expect(args[0]).to(equal(self.local_binary_path))

    def test_launches_correct_executable(self):
        self.create_fake_archive()
        BrowserStackTunnel()
        assert self.popen_spy.call_history, "popen was not called."
        args, kwargs = self.popen_spy.call_history[-1]
        assert args, "popen was called without arguments"
        command_parts = args[0]
        expect(command_parts[0]).to(equal(self.join_path(self.local_binary_path, self.local_binary_filename)))

    def extract_popen_arguments(self):
        assert self.popen_spy.call_history, "popen was not called."
        args, kwargs = self.popen_spy.call_history[-1]
        assert args, "popen was called without arguments"
        return args[0]

    def extract_launch_command(self):
        return " ".join(self.extract_popen_arguments())

    def test_launches_executable_with_access_key_as_first_arg(self):
        access_key = "LOVELY-SPAM"
        self.context.set_env(BROWSERSTACK_ACCESS_KEY=access_key)
        self.create_fake_archive()
        BrowserStackTunnel()
        args = self.extract_popen_arguments()
        assert len(args) > 2, "Expected at least 2 arguments in %s" % (args)
        expect(args[1]).to(equal(access_key))

    def test_launches_executable_with_stdout_pipe(self):
        self.create_fake_archive()
        BrowserStackTunnel()
        assert self.popen_spy.call_history, "popen was not called."
        args, kwargs = self.popen_spy.call_history[-1]
        expect(kwargs).to(contain_key_with_value("stdout", subprocess.PIPE))

    def extract_local_id(self):
        pat = re.compile("--local-identifier ([^ ]*)")
        mat = pat.search(self.extract_launch_command())
        assert mat, "local-identifier was not specified"
        return mat.group(1)

    def test_launches_executable_with_random_local_id(self):
        self.create_fake_archive()
        BrowserStackTunnel()
        first = self.extract_local_id()
        BrowserStackTunnel()
        second = self.extract_local_id()
        expect(second).not_to(equal(first))

    def test_exposes_local_id(self):
        self.create_fake_archive()
        sut = BrowserStackTunnel()
        expect(sut.local_identifier).to(equal(self.extract_local_id()))

    def test_launches_executable_with_stderr_to_stdout(self):
        self.create_fake_archive()
        BrowserStackTunnel()
        assert self.popen_spy.call_history, "popen was not called."
        args, kwargs = self.popen_spy.call_history[-1]
        expect(kwargs).to(contain_key_with_value("stderr", subprocess.STDOUT))

    def test_complains_if_access_key_is_not_configured(self):
        self.context.unset_env("BROWSERSTACK_ACCESS_KEY")
        self.create_fake_archive()
        expect(BrowserStackTunnel).to(raise_ex(InvalidConfiguration))

    def test_raises_exception_if_process_terminates(self):
        self.fake_popen.returncode = 0
        self.create_fake_archive()
        expect(BrowserStackTunnel).to(raise_ex(BrowserStackTunnelClosed))

    def test_ignores_busy_file_on_write_attempt(self):
        e = OSError("intentional")
        e.errno = errno.ETXTBSY
        self.context.inject(open, func_that_raises(e))
        self.create_fake_archive()
        expect(BrowserStackTunnel).not_to(raise_ex(OSError))

    def test_raises_other_os_error_on_write_attempt(self):
        e = OSError("intentional")
        e.errno = errno.ETXTBSY + 1
        self.context.inject(open, func_that_raises(e))
        self.create_fake_archive()
        expect(BrowserStackTunnel).to(raise_ex(OSError))

    def test_raises_other_exception_on_write_attempt(self):
        class FakeException(Exception):
            pass

        self.context.inject(open, func_that_raises(FakeException("intentional")))
        self.create_fake_archive()
        expect(BrowserStackTunnel).to(raise_ex(FakeException))


if "__main__" == __name__:
    main()
