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
                yamlplugin add COMMAND [--dryrun] [-q]
                yamlplugin delete COMMAND [--dryrun] [-q]
                yamlplugin list [--output=FORMAT] [-q]

            Arguments:

                FORMAT   format is either yaml, json, or list [default=yaml]

            Options:

                -q        stands for quiet and suppresses additional messages

            Description:

                Please note that adding and deleting plugins requires restarting
                cm to activate them

                yamlplugin list

                    lists the plugins in the yaml file

                yamlplugin add COMMAND
                yamlplugin delete COMMAND

                    cmd3 contains a ~/.cloudmesh/cmd3.yaml file.
                    This command will add/delete a plugin for a given command
                    that has been generated with cm-generate-command
                    To the yaml this command will add to the modules

                        - cloudmesh_COMMAND.plugins

                    where COMMAND is the name of the command. In case we add
                    a command and the command is out commented the comment
                    will be removed so the command is enabled.


            Example:

                yamlplugin add pbs
        """
        # pprint(arguments)

        quiet = arguments["-q"]

        if arguments["list"]:

            if arguments["--output"] == "yaml":
                plugins_object = command_yamlplugin(quiet=quiet)
                print(plugins_object.config.yaml())
            elif arguments["--output"] == "json":
                plugins_object = command_yamlplugin(quiet=quiet)
                print(plugins_object.config)
            elif arguments["--output"] == "list":
                plugins_object = command_yamlplugin(quiet=quiet)
                print(plugins_object.config["cmd3"]["modules"])
            if arguments["--output"] is None:
                plugins_object = command_yamlplugin(quiet=quiet)
                print(plugins_object)

        elif arguments["add"]:

            plugins_object = command_yamlplugin()
            plugins_object.add(arguments["COMMAND"],
                               dryrun=arguments["--dryrun"])


        elif arguments["delete"]:

            plugins_object = command_yamlplugin()
            plugins_object.delete(arguments["COMMAND"],
                               dryrun=arguments["--dryrun"])

        else:
            Console.error("unknown option.")


if __name__ == '__main__':
    command = cm_shell_yamlplugin()
    command.do_yamlplugin("iu.edu")
    command.do_yamlplugin("iu.edu-wrong")
