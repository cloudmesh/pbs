from __future__ import print_function
import os
from cmd3.console import Console
from cmd3.shell import command

from cloudmesh_pbs.pbs import PBS
from pprint import pprint
from cloudmesh_base.tables import dict_printer

class cm_shell_pbs:

    def activate_cm_shell_pbs (self):
        self.register_command_topic('mycommands', 'qstat')

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
            
            try:
                pbs = PBS(deploy=True)
                if arguments["-a"]:
                    r = pbs.qstat(host, user=False)
                else:
                    r = pbs.qstat(host)
                Console.info("machine " + host + " has been found. ok.")

                if len(arguments['ATTRIBUTES']) != 0 and not arguments['--view']:
                    r = PBS.list(r, arguments['ATTRIBUTES'])
                elif arguments['--view']:
                    view = arguments['VIEW']
                    attributes = pbs.data.get("cloudmesh.pbsview.{0}".format(view))
                    r = PBS.list(r, attributes)
                
            except Exception, e:
                Console.error("machine " + host + " not reachable. error.")
                print (e)
            if len(r.keys()) == 0:
                Console.info("No jobs found")
            else:
                if arguments['--output'] == 'dict' or None:
                    pprint (r)
                else:
                    print(dict_printer(r))
                                
                
        # shell_command_open_ssh(arguments)
        pass


     
if __name__ == '__main__':
    command = cm_shell_pbs()
    command.do_pbs("iu.edu")
    command.do_pbs("iu.edu-wrong")
