from cloudmesh_pbs.PBSScriptWrapper import \
  Wrapper, \
  Status

from unittest import TestCase
from tempfile import NamedTemporaryFile, mkdtemp
from textwrap import dedent
import os
import os.path
import subprocess


class TestableScript(object):
    def __init__(self, script=None, status=None, stdout=None, stderr=None):
        self.script = script
        self.status = status
        self.stdout = stdout
        self.stderr = stderr

    def write(self, fd):
        fd.write(self.script)



class WorkerResult(object):
    def __init__(self, status=None, stdout=None, stderr=None):
        def load(path):
            with open(path) as fd:
                return fd.read().strip()

        self.status = load(status)
        self.stdout = load(stdout)
        self.stderr = load(stderr)


class Worker(object):
    "Dummy to test script execution/input/output/status"

    def __init__(self):
        self.workarea = mkdtemp()

    def __del__(self):
        import shutil
        shutil.rmtree(self.workarea)

    def __call__(self, wrapped):
        wrapped.entrypoint.write(self.workarea)
        wrapped.wrapped.write(self.workarea)
        os.chdir(self.workarea)
        cmd = './{}'.format(wrapped.entrypoint.name)
        subprocess.check_call(cmd)
        return WorkerResult(status=wrapped.status,
                            stdout=wrapped.stdout,
                            stderr=wrapped.stderr)


class TestWrapper(TestCase):

    def setUp(self):
        self.wrapper = Wrapper(bash_location='/bin/sh')
        self.script  = TestableScript(
            script=dedent("""\
              #!/bin/sh
              #PBS -q debug
              #PBS -l nodes=1:ppn=1

              echo "hello world"
              echo "this is to stderr" >&2
              """),
            status=Status.success,
            stdout='hello world',
            stderr='this is to stderr')

        self.script_fd = NamedTemporaryFile()
        self.script.write(self.script_fd)
        self.script_fd.seek(0)
        self.script_path = self.script_fd.name

    def tearDown(self):
        self.script_fd.close()


    @property
    def wrapped(self):
        return self.wrapper.wrap(self.script_path)

    def test_wrap_works(self):
        "Wrapper should work"
        wrapped = self.wrapped
        self.assertIsNotNone(wrapped)

    def test_names(self):
        w = self.wrapped
        name = os.path.basename(self.script_path)
        self.assertEquals(w.entrypoint.name, name)
        self.assertEquals(w.wrapped.name, 'wrapped-{}'.format(name))

    def test_run(self):
        w = Worker()
        r = w(self.wrapped)
        self.assertEquals(r.status, self.script.status)
        self.assertEquals(r.stdout, self.script.stdout)
        self.assertEquals(r.stderr, self.script.stderr)
