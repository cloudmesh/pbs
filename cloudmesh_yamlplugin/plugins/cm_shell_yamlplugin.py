from __future__ import print_function
import os
from cmd3.console import Console
from cmd3.shell import command

from cloudmesh_yamlplugin.command_yamlplugin import command_yamlplugin
from pprint import pprint

class cm_shell_yamlplugin:

    def activate_cm_shell_yamlplugin(self):
        self.register_command_topic('cmd3', 'yamlplugin')

    @command
    def do_yamlplugin(self, args, arguments):
        """
        ::

            Usage:
                yamlplugin add COMMAND [--dryrun]
                yamlplugin delete COMMAND [--dryrun]
                yamlplugin disable COMMAND [--dryrun]
                yamlplugin list [--output=FORMAT]

            Description:

                Please note that adding and deleting plugins requires restarting
                cm to activate them

                yamlplugin list

                    lists the plugins in the yaml file

                yamlplugin add/delete COMMAND
                yamlplugin delete COMMAND

                    cmd3 contains a ~/.cloudmesh/cmd3.yaml file.
                    This command will add/delete a plugin for a given command
                    that has been generated with cm-generate-command
                    To the yaml this command will add to the modules

                        - cloudmesh_COMMAND.plugins

                    where COMMAND is the name of the command. In case we add
                    a command and the command is out commented the comment
                    will be removed so the command is enabled.

                yamlplugin disable COMMAND

                    sometimes it is beneficial to actually not delete the module
                    from the yaml file but out-comment. This way it can using add
                    will first check if it it out commented and remove the comment
                    to enable it

            Example:

                yamlplugin add pbs
        """
        # pprint(arguments)

        if arguments["list"]:

            if arguments["--output"] == "yaml":
                plugins_object = command_yamlplugin()
                print(plugins_object.config.yaml())
            elif arguments["--output"] == "json":
                plugins_object = command_yamlplugin()
                print(plugins_object.config)
            if arguments["--output"] is None:
                plugins_object = command_yamlplugin()
                print(plugins_object)

        elif arguments["add"]:

            plugins_object = command_yamlplugin()
            plugins_object.add(arguments["COMMAND"],
                               dryrun=arguments["--dryrun"])


        elif arguments["disable"]:
            print("disable")
        elif arguments["enable"]:
            print("disable")
        else:
            Console.error("unkown option.")
        pass

if __name__ == '__main__':
    command = cm_shell_yamlplugin()
    command.do_yamlplugin("iu.edu")
    command.do_yamlplugin("iu.edu-wrong")
