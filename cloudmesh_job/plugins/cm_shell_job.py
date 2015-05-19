from __future__ import print_function

# from cloudmesh_job.cm_jobdb import JobDB
from cmd3.console import Console
from cmd3.shell import command


class cm_shell_job:
    database = None

    def activate_cm_shell_job(self):
        self.register_command_topic('HPC', 'job')

    @command
    def do_job(self, args, arguments):
        """
        ::

            Usage:

                job server start
                job server stop
                job server clean
                job server kill
                job server deploy
                job stat
                job list
                job insert NAME [HOST] [OPTIONS] [INPUT_FILES] [OUTPUT_FILES]
                job find --name=NAME
                job find --attribute=ATTRIBUTE --value=VALUE
                job delete --name=NAME


            manages a job catalog to submit them to a computation cloud or Grid.

            Description:

                job server start

                    starts the job server

                job server stop

                    stops the job server

                job server clean

                    removes all data in the job server and does a graceful clean, e.g deletes all scheduled jobs

                job server kill

                    kills just the job server, but does not delete the jobs from the schedulers.
                    this command should not be called in normal circumstances.

                job set GROUP

                    sets the default job group

                job add  GROUP TODO

                    adds a job to a group

                job server start

                    starts the server

                job server stop

                    stops the server

                job stat

                    prints a simple statistics of the jobs

                job list [--output=OUTPUT]

                    lists the jobs in the format specified

                job insert NAME [HOST] [OPTIONS] [INPUT_FILES] [OUTPUT_FILES]

                    inserts the job with the name into the job database. Options,
                    input and output files could be specified

                job find --name=NAME

                    find the job with the given name

                job find --attribute=ATTRIBUTE --value=VALUE

                    find jobs that match the given attribute.

                job delete --name=NAME

                    delete the job with the specified name.

                THE FOLLOWING IS NOT YET DEFINED OR MAY CHANGE

                job add TODO

                    ... not yet sure what in the rest of the command

                    adds a job to the job server and returns its id

                job last

                    returns the last job added to the server

                job delete ID

                    deletes the job from the job server and cancels it if it is scheduled for execution.

                job info ID

                    give the info of a job

                job submit ID HOST

                    submits the job with the given ID to the host

                job list GROUP

                    lists the jobs in the group

                job status [ID | GROUP]

                    list the status of a single job or the status of all jobs in the group

                job status statistics

                    list the statistics of the jobs in the job server (e.g. for the states)



        """

        if arguments["server"] and arguments["start"]:

            Console.ok("job server start")

        elif arguments["server"] and arguments["stop"]:

            Console.ok("job server stop")

        elif arguments["server"] and arguments["clean"]:

            Console.ok("job server clean")

        elif arguments["server"] and arguments["kill"]:

            Console.ok("job server kill")

        elif arguments["server"] and arguments["deploy"]:

            Console.ok("job server deploy")

        elif arguments["stat"]:

            Console.ok("job stat")

        elif arguments["list"]:

            output = arguments["--output"]

            Console.ok("lists the jobs in the format specified")

        elif arguments["insert"]:

            name = arguments["NAME"]
            host = arguments["HOST"]
            options = arguments["OPTIONS"]
            input_files = arguments["INPUT_FILES"]
            output_file = arguments["OUTPUT_FILES"]

            Console.ok("insert")

        elif arguments["find"] and arguments["--name"]:

            name = arguments["NAME"]

            Console.ok("find the job with the given name")

        elif arguments["find"] and arguments["--attribute"] and arguments["--value"]:

            name = arguments["NAME"]
            attribute = arguments["--attribute"]
            value = arguments["--value"]

            Console.ok("job find --attribute=ATTRIBUTE --value=VALUE")

        elif arguments["delete"] and arguments["NAME"]:

            name = arguments["NAME"]

            Console.ok("delete the job with the given name")

        pass


if __name__ == '__main__':
    command = cm_shell_job()
    command.do_job()