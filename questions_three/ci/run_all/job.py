from datetime import datetime
from subprocess import Popen, PIPE, STDOUT
import sys

from twin_sister import dependency


# Flush process output streams every this number of seconds
FLUSH_INTERVAL = 3 * 60


def now():
    return dependency(datetime).now()


class Job:
    def __init__(self, *, path_to_script, output_stream):
        self._last_flush = None
        self._output_stream = output_stream
        self._path_to_script = path_to_script
        self._proc = None
        self.name = path_to_script

    def _flush(self):
        output = self._proc.stdout.read().decode('utf-8')
        if output.strip():
            self._output_stream.write(
                '\n** From %s **\n' % self._path_to_script)
            self._output_stream.write('%s\n' % output)
            self._output_stream.flush()
        self._last_flush = now()

    def _should_flush(self):
        return (now() - self._last_flush).total_seconds() > FLUSH_INTERVAL

    def run(self):
        self._proc = dependency(Popen)(
            [dependency(sys.executable), self._path_to_script],
            stderr=STDOUT, stdout=PIPE)
        self._last_flush = now()

    def kill(self):
        self._proc.kill()

    def poll(self):
        """
        Flush output if necessary.
        Periodic flushing prevents us from deadlocking if an output
          buffer becomes full.
        Return process exit code (or None if still running)
        """
        code = self._proc.poll()
        if code is not None or self._should_flush():
            self._flush()
        return code
