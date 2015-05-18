#BUG: this import statement must be in the class wrapped in a boolean to see if the command was
# initialized. this allows the shellto start without dependency on mongo
import cm_mongodb

class cm_shell_jobs:
	database = None

    def activate_cm_shell_jobs(self):
        self.register_command_topic('mycommands', 'jobs')

    # TODO THE COMMAND SEEMS COMPLICATED
    # TODO the parsing of REQARG could be simplified while writing the commandout
    # TODO maybe we need to split in multiple commands such as
    # TODO the following may be easier


    """
        job server start
        job server stop
        job server clean

            removes all data in the job server and does a graceful clean, e.g deletes all scheduled jobs

        job server kill

            kills just the job server, but does not delete the jobs from the scheudlers.
            thsi command should not be called in normal circumstances.

        job set GROUP

            sets the defualt job group

        job add  GROUP ...

            adds a job to a group

        job server start

            starts the server

        job server stop

            stops the server

        job add  ...

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

            list the status of a single job or the status of all jobe sin the group

        job status statistics

            list the statistics of the jobs in the job server (e.g. for the states)


    """
    @command
    def do_jobs(self, args, arguments):
        """
        ::

          Usage:
              jobs REQARG1 OPTARG1 OPTARG2 OPTARG3

          Performs various jobs functions explained below

          Arguments:

            REQARG1     Initial function to perform. Possible values: deploy, start, clear, set, delete, list

                        startMongo : deploys mongo instance, OPTARG1 is db_path, OPTARG2 is port, OPTARG3 is log_path
                        stopMongo  : stops mongo instance
                        connect    : either connects to a pre-existing db or creates a new one
                        insertJob  : Creates a new job, requires OPTARG1 to be job_name, OPTARG2 & OPTARG3 are input
                                     file and output file
                        findJobs :   Finds all running jobs, no required parameters but you may provide key_name and
                                     value to return specific jobs
                        deleteJobs : deletes all running jobs, no required parameters but you may provide key_name
                                     and value to delete specific jobs
						numJobs :    prints a count of jobs currently running

            OPTARG1

            OPTARG2

            OPTARG3

          Options:
        """


        if arguments["REQARG1"] == "startMongo":

			self.database = cm_mongodb.db()

			if arguments["OPTARG1"] is not None:
				dbpath = arguments["OPTARG1"]

				if argument["OPTARG2"] is not None:
					dbport = arguments["OPTARG2"]

					if argument["OPTARG3"] is not None:
						logport = arguments["OPTARG3"]
						self.database.startMongo(dbpath, dbport, logport)

					else:
						self.database.startMongo(dbpath, dbport)
				else:
					self.database.startMongo(dbpath)
			else:
				self.database.startMongo()


        elif arguments["REQARG1"] == "stopMongo":

            self.database.stopMongo()


        elif arguments["REQARG1"] == "connect":

			if arguments["OPTARG1"] is not None:
				dbname = arguments["OPTARG1"]
				self.database.connect(dbname)
			else:
				self.database.connect()

        elif arguments["REQARG1"] == "insertJob":

			if argument["OPTARG1"] is not None:
				jobname = argument["OPTARG1"]

				if argument["OPTARG2"] is not None:
					input = argument["OPTARG2"]

					if argument["OPTARG3"] is not None:
						output = argument["OPTARG3"]
						self.database.insertJobs(jobname, input, output)

					else:
						self.database.insertJobs(jobname, input)
				else:
					self.database.insertJobs(jobname)
			else:
				self.database.insertJobs()

        elif arguments["REQARG1"] == "findJobs":

            if argument["OPTARG1"] is not None:
				keyname = argument["OPTARG1"]
				value = argument["OPTARG2"]
				self.database.insertJobs(keyname, value)
			else:
				self.database.insertJobs()


        elif arguments["REQARG1"] == "deleteJobs":

			if argument["OPTARG1"] is not None:
				keyname = argument["OPTARG1"]
				value = argument["OPTARG2"]
				self.database.deleteJobs(keyname, value)
            else:
				self.database.deleteJobs()

		elif arguments["REQARG1"] == "findJobs":

            if argument["OPTARG1"] is not None:
				keyname = argument["OPTARG1"]
				value = argument["OPTARG2"]
				self.database.insertJobs(keyname, value)
			else:
				self.database.insertJobs()


        elif arguments["REQARG1"] == "numJobs":

			if argument["OPTARG1"] is not None:
				keyname = argument["OPTARG1"]
				value = argument["OPTARG2"]
				self.database.numJobs(keyname, value)
            else:
				self.database.numJobs()

		elif arguments["REQARG1"] == "UpdateJobEndTime":

			jobid = argument["OPTARG1"]
			endtime = argument["OPTARG2"]
			self.database.numJobs(jobid, endtime)

		elif argument["REQARG1"] == "insertJobObject":

			job = argument["OPTARG1"]
			self.database.insertJobObject(job)

        pass

if __name__ == '__main__':
    command = cm_shell_jobs()
    command.do_jobs()