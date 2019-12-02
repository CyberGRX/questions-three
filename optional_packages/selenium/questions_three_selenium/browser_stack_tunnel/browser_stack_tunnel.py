import errno
from io import BytesIO
import os
from random import randint
from subprocess import PIPE, Popen, STDOUT
import time
from zipfile import ZipFile

from questions_three.constants import TestEvent
from questions_three.event_broker import EventBroker
from questions_three.exceptions import InvalidConfiguration
from questions_three.http_client import HttpClient
from questions_three.logging import logger_for_module
from questions_three.module_cfg import config_for_module
from twin_sister import dependency

from questions_three_selenium.exceptions import BrowserStackTunnelClosed


def create_shared_directories():
    config = config_for_module(__name__)
    path, _ = dependency(os).path.split(config.browserstack_local_binary)
    dependency(os).makedirs(path, exist_ok=True)


def current_pid():
    return dependency(os).getpid()


def extract_from_zip(archive, file_name):
    zf = ZipFile(BytesIO(archive))
    with zf.open(name=file_name) as f:
        artifact = f.read()
    return artifact


def launch_executable(local_identifier):
    config = config_for_module(__name__)
    key = config.browserstack_access_key
    if not key:
        raise InvalidConfiguration(
            '$BROWSERSTACK_ACCESS_KEY is not configured')
    proc = dependency(Popen)(
        [
            config.browserstack_local_binary, key,
            '--local-identifier', local_identifier],
        stdout=PIPE, stderr=STDOUT)
    if None != proc.returncode:  # noqa: E711 spies trip "is" up.
        raise BrowserStackTunnelClosed('Process terminated unexpectedly')
    return proc


def retrieve_zip_archive_from_nexus():
    config = config_for_module(__name__)
    http = dependency(HttpClient)()
    return http.get(config.browserstack_local_binary_zip_url).content


def save_executable(executable):
    config = config_for_module(__name__)
    log = logger_for_module(__name__)
    os_module = dependency(os)
    fopen = dependency(open)
    filename = config.browserstack_local_binary
    # HACK: Avoid a race condition: don't rewrite the same file (QA-291)
    if os_module.path.exists(filename):
        with fopen(filename, 'rb') as f:
            if executable == f.read():
                return
    try:
        with fopen(filename, 'wb') as f:
            f.write(executable)
        os_module.chmod(filename, 0o775)
    except OSError as e:
        if e.errno == errno.ETXTBSY:
            log.warning(
                'Failed to update %s because it is busy' % filename)
        else:
            raise


class BrowserStackTunnel:

    def __init__(self):
        self.local_identifier = str(randint(0, 10**9))
        create_shared_directories()
        self._open_new_tunnel()
        EventBroker.subscribe(
            event=TestEvent.suite_ended, func=self.on_suite_ended)

    def on_suite_ended(self, **kwargs):
        self.close()

    def close(self):
        self._tunnel_proc.terminate()

    def _open_new_tunnel(self):
        config = config_for_module(__name__)
        path, filename = dependency(os).path.split(
            config.browserstack_local_binary)
        # Race condition mitigation.
        # If the executable does not exist, we're at risk of multiple
        # processes trying to create it at the same time.
        # Sleep for a random interval to get any such processes out of sync.
        if not dependency(os).path.exists(path):
            dependency(time.sleep)(randint(0, 10000)/1000)
        zip_archive = retrieve_zip_archive_from_nexus()
        executable = extract_from_zip(zip_archive, filename)
        save_executable(executable)
        self._tunnel_proc = launch_executable(
            local_identifier=self.local_identifier)
