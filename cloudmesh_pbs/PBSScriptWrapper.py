"""Wrap the PBS script with another script that captures stdout and
stderr, and provides support for checking the status of the job.
"""

import shlex
import pipes
from collections import namedtuple
import os.path
from textwrap import dedent
import os
import stat


PBSScriptParserResult = namedtuple(
    'PBSScriptParserResult',
    ['shebang',
     'directives',
     'script'])


class PBSScriptParser(object):
    def __init__(self):
        # the shebang
        #
        # do not set the default to a string: this is an important
        # part of the script and if we make a bad assumption then
        # hard-to-track errors will by likely.
        # instead, better to fail upfront if no shebang is provided.
        self._shebang = None

        # directives is a list of the qsub directives embedded in the script:
        # eg:
        # #PBS -l nodes=1:ppn=1
        self._directives = list()

        # these are the rest of the contents of the script
        self._lines = list()

        # position
        self._line_counter = 1


    def is_shebang(self, line):
        """
        # TODO unclear why two different vars are used and not just line
        # TODO why not classmethod?
        test if the line starts with #!

        :param line: the line to test
        :return: True if it starts with #!
        """
        return self._line_counter == 1 and line.startswith('#!')

    def handle_shebang(self, line):
        """
        strips liading and trailing spaces from the line and assigns it internally
        :param line:  the line
        """
        self._shebang = line.strip()

    def handle_directive(self, line, prefix='#PBS'):
        assert line.startswith(prefix)
        stripped = line.lstrip(prefix)
        directives = shlex.split(stripped)

        if not self._directives:
            self._directives.append(prefix)
        self._directives.extend(directives)

    def is_directive(self, line):
        """
        verifies if the line starts with #PBS

        :param line: the line
        :return: True if it starts with #PBS
        """
        return line.startswith('#PBS')

    def handle_script(self, line):
        """
        TODO: name unclear

        appends the line to the script

        :param line: the line
        """
        self._lines.append(line)

    def result(self):
        # see comment in __init__ for why
        assert self._shebang is not None
        script = ''.join(self._lines)
        return PBSScriptParserResult(
            shebang=self._shebang,
            directives=self._directives,
            script=script)

    def _parse_line(self, line):
        if self.is_shebang(line):
            self.handle_shebang(line)
        elif self.is_directive(line):
            self.handle_directive(line)
        else:
            self.handle_script(line)

        self._line_counter += 1

    def _parse_lines(self, line_itr):
        for line in line_itr:
            self._parse_line(line)

        return self.result()

    def _parse_file(self, fd):
        return self._parse_lines(fd)

    def _parse_path(self, path):
        """
        TODO why not simply rename this to load
        :param path:
        :return:
        """
        with open(path, 'r') as fd:
            return self._parse_file(fd)

    def parses(self, script_string):
        return self._parse_lines(script_string.split('\n'))

    def parse(self, path_or_file):
        if isinstance(path_or_file, str):
            return self._parse_path(path_or_file)
        elif isinstance(path_or_file, file):
            return self._parse_file(path_or_file)
        else:
            raise ValueError('Unsupport type {}'.format(path_or_file))

    # TODO lots of parsing functions, but which wone do we realy need,
    # which once are internal. rename internal with _


class Script(object):

    def __init__(self,
                 name,
                 contents,
                 mode=stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH):
        self._name = name
        self._contents = contents
        self._mode = mode

    @property
    def name(self):
        "Name (or path) of the script"
        return self._name

    @property
    def script(self):
        "The script body"
        return self._contents

    @property
    def mode(self):
        "The script execution bits (passed to `os.chmod`"
        return self._mode

    @mode.setter
    def mode(self, bits):
        self._mode = bits

    def write(self, directory):
        "Writes the script into a file name ``name`` in the directory"
        with open(os.path.join(directory, self.name), 'w') as fd:
            fd.write(self.script)
            os.chmod(fd.name, self.mode)
        # TODO improve mode passing in open call as to avoid wrong permissions

class Status(object):
    "The various states of a job"

    started = 'started'
    success = 'success'
    failure = 'failure'

    # TODO: this does not follow our states we defined in paper

class WrappedScript(object):

    # TODO Rename to CloudmeshHPCscript?

    def __init__(self,
                 entrypoint,
                 wrapped,
                 status='STATUS.txt',
                 stdout='STDOUT.txt',
                 stderr='STDERR.txt'):
        self._entrypoint = entrypoint
        self._wrapped = wrapped
        self.status = status
        self.stdout = stdout
        self.stderr = stderr

    @property
    def entrypoint(self):
        """The :class:`Script` that is the main entrypoint (the wrapper)"""
        return self._entrypoint

    @property
    def wrapped(self):
        """The wrapped script"""
        return self._wrapped

    def write(self, directory):
        """
        TODO documentation
        :param directory:
        :return:
        """
        self.entrypoint.write(directory)
        self.wrapped.write(directory)
        return [os.path.join(directory, name)
                for name in [self.entrypoint.name,
                             self.wrapped.name]]


class Wrapper(object):

    def __init__(self, bash_location='/bin/bash'):
        """
        TODO documentation
        :param bash_location:
        :return:
        """
        # sometimes /usr/bin may not exist on grids
        self.shebang = '#!' + bash_location
        self.stdout = 'STDOUT.txt'
        self.stderr = 'STDERR.txt'
        self.status = 'STATUS.txt'

    def wrap(self, path_to_script, arguments=None):
        """
        TODO documentation
        :param path_to_script:
        :param arguments:
        :return:
        """
        name = os.path.basename(path_to_script)
        name_wrapped = 'wrapped-{}'.format(name)

        args = arguments or list()

        parser = PBSScriptParser()
        tokens = parser.parse(path_to_script)

        wrapped_script = tokens.shebang + '\n' + tokens.script
        wrapped = Script(name_wrapped, wrapped_script)

        directives = ' '.join(tokens.directives)
        newscript_contents = dedent("""\
        {shebang}
        {directives}

        echo {state_started} > {state}
        ./wrapped-{old_name} {args} >{stdout} 2>{stderr}
        exit_code=$?

        if [ $exit_code -eq 0 ];then
            echo {state_success} > {state}
        else
            echo {state_failure} > {state}
        fi
        """.format(shebang=self.shebang,
                   directives=directives,
                   old_name=name,
                   args=' '.join(map(pipes.quote, args)),
                   state=self.status,
                   stdout=self.stdout,
                   stderr=self.stderr,
                   state_started=Status.started,
                   state_success=Status.success,
                   state_failure=Status.failure
                   ))

        newscript = Script(name, newscript_contents)

        return WrappedScript(newscript, wrapped,
                             status=self.status,
                             stdout=self.stdout,
                             stderr=self.stderr)
