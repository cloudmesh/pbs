"""Wrap the PBS script with another script that captures stdout and
stderr, and provides support for checking the status of the job.
"""

import shlex
from collections import namedtuple
import os.path
from textwrap import dedent


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
        # wierd and hard-to-track-down errors will likely crop up.
        # instead, better to fail upfront if no shebang is provided.
        self._shebang = None

        # directives is a list of the qsub directives embedded in the script:
        # eg:
        #  #PBS -l nodes=1:ppn=1
        self._directives = list()

        # these are the rest of the contents of the script
        self._lines = list

    def handle_directive(self, line, prefix='#PBS'):
        assert line.startswith(prefix)
        stripped = line.lstrip(prefix)
        directives = shlex.split(stripped)

        if not self._directives:
            self._directives.append(prefix)
        self._directives.extend(directives)

    def is_directive(self, line):
        return line.startswith('#PBS')

    def handle_script(self, line):
        self._lines.append(line)

    def result(self):
        # see comment in __init__ for why
        assert self._shebang is not None
        script = '\n'.join(self._lines)
        return PBSScriptParserResult(shebang=self._shebang,
                                     directives=self._directives,
                                     script=script)

    def _parse_line(self, line):
        if self.is_directive(line):
            self.handle_directive(line)
        else:
            self.handle_script(line)

    def _parse_lines(self, line_itr):
        for line in line_itr:
            self._parse_line(line)

        return self.result()

    def _parse_file(self, fd):
        return self._parse_lines(fd)

    def _parse_path(self, path):
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



class Script(object):
    def __init__(self, name, contents):
        self._name = name
        self._contents = contents

    @property
    def name(self):
        "Name (or path) of the script"
        return name

    @property
    def script(self):
        "The script body"
        return self._contents

class Status(object):
    "The various states of a job"

    started = 'started'
    success = 'success'
    failure = 'failure'


class WrappedScript(object):
    def __init__(self, entrypoint, wrapped):
        self._entrypoint = entrypoint
        self._wrapped = wrapped

    @property
    def entrypoint(self):
        "The :class:`Script` that is the main entrypoint (the wrapper)"
        return self._entrypoint

    @property
    def wrapped(self):
        "The wrapped script"
        return self._wrapped


class Wrapper(object):
    def __init__(self, bash_location='/bin/bash'):
        # sometimes /usr/bin may not exist on grids
        self._shebang = '#!' + bash_location
        self._stdout = 'STDOUT.txt'
        self._stderr = 'STDERR.txt '
        self._status = 'STATUS.txt'


    def wrap(self, path_to_script):
        name = os.path.basename(path_to_script)

        parser = PBSScriptParser()
        tokens = parser.parse(path_to_script)

        wrapped = Script(name, tokens.script)

        directives = ' '.join(tokens.directives)
        newscript_contents = dedent("""\
        {shebang}
        {directives}

        echo {state_started} > {state}
        ./wrapped-{old_name}.sh >{stdout} 2>{stderr}
        exit_code=$?

        if [ $exit_code -eq 0 ];then
            echo {state_success} > {state}
        else
            echo {state_failure} > {state}
        fi
        """.format(shebang=self._shebang,
                   directives=directives,
                   old_name=name,
                   state=self._status,
                   state_started=Status.started,
                   state_success=Status.success,
                   state_failure=Status.failure
                   ))

        newscript = Script(name, newscript_contents)

        return WrappedScript(newscript, wrapped)


# TODO: add tests
    
