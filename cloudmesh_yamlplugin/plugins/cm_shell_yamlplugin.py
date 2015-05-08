from __future__ import print_function
import os
from cmd3.console import Console
from cmd3.shell import command

from cloudmesh_yamlplugin.command_yamlplugin import command_yamlplugin


class cm_shell_yamlplugin:

    def activate_cm_shell_yamlplugin(self):
        self.register_command_topic('mycommands', 'yamlplugin')

    @command
    def do_yamlplugin(self, args, arguments):
        """
        ::

            Usage:

                yamlplugin add --command COMMAND
                yamlplugin add --package PACKAGE

                yamlplugin delete --command COMMAND
                yamlplugin delete --package PACKAGE

                yamlplugin disable --command COMMAND
                yamlplugin disable --package PACKAGE

                yamlplugin list

                yamlplugin view

            Description:

                Please note that adding and deleting plugins requires restarting
                cm to activate them

                yamlplugin list

                    lists the plugins in the yaml file

                yamlplugin list

                    lists the plugins in the yaml file

                yamlplugin --command add/delete COMMAND
                yamlplugin delete --command COMMAND

                    cmd3 contains a ~/.cloudmesh/cmd3.yaml file.
                    This command will add/delete a plugin for a given command
                    that has been generated with cm-generate-command
                    To the yaml this command will add to the modules

                        - cloudmesh_COMMAND.plugins

                    where COMMAND is the name of the command. In case we add
                    a command and the command is out commented the comment
                    will be removed so the command is enabled.

                yamlplugin add --package PACKAGE
                yamlplugin delete --package PACKAGE

                    This command adds/delete the package name

                        - PACKAGE.plugins

                    To the cmd3.yaml file

                yamlplugin disable --command COMMAND
                yamlplugin disable --package PACKAGE

                    sometimes it is beneficial to actually not delete the module
                    from the yaml file but out comment. THis way it can using add
                    will first check if it it out commended and remove the comment
                    to enable it

            Example:

                yamlplugin add pbs
        """
        # pprint(arguments)

        if arguments["NAME"] is None:
            Console.error("Please specify a host name")
        else:
            host = arguments["NAME"]
            Console.info("trying to reach {0}".format(host))
            status = command_yamlplugin.status(host)
            if status:
                Console.info("machine " + host + " has been found. ok.")
            else:
                Console.error("machine " + host + " not reachable. error.")
        pass

if __name__ == '__main__':
    command = cm_shell_yamlplugin()
    command.do_yamlplugin("iu.edu")
    command.do_yamlplugin("iu.edu-wrong")
