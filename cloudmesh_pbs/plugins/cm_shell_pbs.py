from __future__ import print_function
import os
from cmd3.console import Console
from cmd3.shell import command

from cloudmesh_pbs.OpenPBS import OpenPBS
from pprint import pprint
from cloudmesh_base.tables import dict_printer


class cm_shell_pbs:
    def activate_cm_shell_pbs(self):
        self.register_command_topic('mycommands', 'pbs')
        self.register_command_topic('mycommands', 'queue')
        self.register_command_topic('mycommands', 'qstat')

    @command
    def do_pbs(self, args, arguments):
        """
        ::

            Usage:

                pbs mongo find status=STATE [--short|--all|--limit=COUNT]
                pbs mongo add DICT
                pbs mongo summary

                pbs mongo schema [-list] [--format=yaml|dict]
                pbs mongo schema [--name=NAME][--format=yaml|dict]

            Description:

                pbs mongo find [host=HOST] [status=STATE] [--short|--all|--limit=COUNT]

                    issues a specific query while focussing on those elements with a specific state or host.
                    if neither host or status is specified the command fails

                pbs mongo add DICT

                    add the object specified as a string to the cloudmesh_job

                pbs mongo summary

                    provides an easy to read summary of the objects.
                    For example includes a count of hwo many objects are in which state
                    How many objects are in the cloudmesh_job (of a particular kind)
                    ...

                pbs mongo schema [-list] [--format=yaml|dict]

                    lists the object name schema in the format specified

                pbs mongo schema [--name=NAME][--format=yaml|dict]

                    list the object attributes with the given name in the format specified.

            Arguments:

                ... TODO ...

                set default values for PATH and others as needed.

            Format:

                config.yaml

                mongo:
                    port: 27017
                    dbpath: ~/.cloudmesh/pbs/data_mongo.db
                    logpath: ~/.cloudmesh/pbs/data_mongo.log
        """
        return

    @command
    def do_queue(self, args, arguments):
        """
        ::

            Usage:

                queue stat [--host=HOST] ARGUMENTS
                queue sub [--host=HOST] ARGUMENTS
                queue default --host=HOST [--queue=NAME]

            Description:

                queue stat [--host=HOST] ARGUMENTS

                    executes a qstat command on the given host

                queue sub [--host=HOST] ARGUMENTS

                    executes a qstat command on the given host

                queue default --host=HOST [--queue=NAME]

                    sets the default hos or the default queue for a host

            Example:

                cm queue default --host=india --queue=batch

                    sets the default queue for india to batch.
                    This does not set the india host to be the
                    default queue. This must be explicitly set
                    with the next command

                cm queue default --host=india

                    sets the defulat queue to india. if host is
                    not specified india is used
        """
        return

    @command
    def do_qstat(self, args, arguments):
        """
        ::

          Usage:
            qstat HOST [-a]  [(--view VIEW | ATTRIBUTES...)] [--output=(dict|table)]

          tests via ping if the host ith the give NAME is reacahble

          Arguments:

            VIEW  the name of the view [default: default].
            HOST      Name of the machine to test

          Options:

             -v       verbose mode

        """

        if arguments["HOST"]:
            host = arguments["HOST"]

            Console.info("trying to reach {0}".format(host))

            if len(arguments['ATTRIBUTES']) == 0 and not arguments['--view']:
                arguments['--view'] = True
                arguments['VIEW'] = 'default'
                # pprint(arguments)

            r = {}
            try:
                pbs = OpenPBS(deploy=True)
                if arguments["-a"]:
                    r = pbs.qstat(host, user=False)
                else:
                    r = pbs.qstat(host)
                Console.info("machine " + host + " has been found. ok.")

                if len(arguments['ATTRIBUTES']) != 0 and not arguments['--view']:
                    r = OpenPBS.list(r, arguments['ATTRIBUTES'])
                elif arguments['--view']:
                    view = arguments['VIEW']
                    attributes = pbs.data.get("cloudmesh.pbsview.{0}".format(view))
                    r = OpenPBS.list(r, attributes)

            except Exception, e:
                Console.error("machine " + host + " not reachable. error.")
                print(e)
            if len(r.keys()) == 0:
                Console.info("No jobs found")
            else:
                if arguments['--output'] == 'dict' or None:
                    pprint(r)
                else:
                    print(dict_printer(r))

        # shell_command_open_ssh(arguments)
        pass


if __name__ == '__main__':
    command = cm_shell_pbs()
    command.do_qstat("india")
    # command.do_qstat("iu.edu-wrong")
