from __future__ import print_function

import subprocess
from cloudmesh_base.ConfigDict import ConfigDict
from cloudmesh_base.tables import dict_printer
from cloudmesh_base.Shell import Shell
from cloudmesh_base.util import banner
from cloudmesh_base.util import path_expand
from cmd3.console import Console
from cloudmesh_base.locations import config_file
import pymongo
from pymongo import MongoClient
import datetime
import os
from pprint import pprint
import sys
import subprocess
import yaml

class JobDB(object):
    database = None
    jobs = None

    def isup(self):
        """
        returns True is mongod is up
        :return: True if mongod is up
        :rtype: boolean
        """
        try:
           command = "nc -z localhost {:}".format(self.port).split(" ")
           result = subprocess.check_output(command)
           up = "succeeded" in result
        except:
            up = False
        return up

    def wait(self):
        """
        waits til the server is up
        :return:
        """
    def pid(self):
        """
        finds the pid of the mongod process
        :return: the pid number or None if not found
        :rtype: int or None
        """
        command = 'ps aux'.split(" ")
        result = subprocess.check_output(command).split('\n')
        for line in result:
            if ('mongod' in line) and str(self.port) in line:
                break
        line = " ".join(line.split())
        columns = line.split(" ")
        try:
            pid = columns[1]
        except:
            pid = None
        return pid

    def load(self, filename="/cloudmesh_pbs.yaml"):
        """
        The configuration for the job db is stored in a yaml
        file. The defualt location is ~/.cloudmesh/cloudmesh_pbs.yaml
        :param filename: the filename of the yaml file
        :type filename: str
        """
        self.filename = config_file(filename)
        self.data = ConfigDict(filename=self.filename)

        self.port = self.data["cloudmesh"]["jobdatabase"]["port"]
        self.db_path = path_expand(self.data["cloudmesh"]["jobdatabase"]["db_path"])
        self.log_file = path_expand(self.db_path + "/dbjobs.log")
        self.dbname = self.data["cloudmesh"]["jobdatabase"]["dbname"]

    def __init__(self, yaml_filename="/cloudmesh_pbs.yaml", info=False):
        """
        Creates an object instance of a job database as defined in the cloudmesh_pbs yaml file

        :param deploy: If True, creates the configuration files
        :param yaml_filename: The cloudmesh pbs yaml file. Defaults to
                              cloudmesh_pbs.yaml
        :return: an object for manageing jobs in the database
        """
        self.load(filename=yaml_filename)
        self.deploy()
        self.info = info

    def deploy(self):
        """
        creates the directories if they do not exist
        """
        try:
            r = Shell.mkdir(self.db_path)
        except Exception, e:
            Console.error("Problem creating the database directory {:}".format(self.db_path))
            print(e)
        try:
            file = open(self.log_file, 'a+')
            file.close()
        except Exception, e:
            Console.error("Problem creating the log file {:}".format(self.log_file))
            print(e)

    # TODO COMBINE WITH __INIT__ ???
    # BUG not a good location for  the data /data
    # BUG not a good location for logpath as we run this in user mode
    # port and location should probably read from cloudmesh_pbs.yaml and values here set to None.see load function


    def ps(self):
        """
        A simple ps command to see if mongodb is running
        """
        os.system("ps aux | fgrep mongod |fgrep -v fgrep")

    def start(self):
        """
        starts the database service
        :return: the pid
        """
        if self.isup():
            _pid = self.pid()
            Console.error("A mongod process on port {:} is already running with pid {:}".format(self.port, _pid))
            return
        else:
            Console.ok("STARTING")
        try:

            mongod = Shell.which("mongod")
            command = [
                mongod,
                "--dbpath", str(self.db_path),
                "--port", str(self.port),
                "--fork",
                "--logpath", str(self.log_file),
                "--bind_ip", "127.0.0.1"
            ]
            print(" ".join(command))
            # a = subprocess.call(command)
            os.system(" ".join(command))
            self.ps()
            Console.ok("MongoDB has been deployed")
            self.info()
            return None  # implement the return of the pid for the process.
            # store the pid in self.pid

        except Exception, e:
            Console.error("we had a problem starting the  mongo daemon")
            print(e)
            Console.error("MongoDB has stopped")
            # TODO remove the exit in final code, for debugging only
            sys.exit()

    def stop(self):
        """
        stops the server
        """
        # TODO: Ryoan use the pid to kill the server or use gracefule shutdown.
        try:
            # command = ["mongod", "--shutdown"]
            command = ["killall", "mongod"]
            print(" ".join(command))
            os.system(" ".join(command))
            Console.ok("MongoDB has been shutdown")
            # os.system("mongod --shutdown")
        except Exception, e:
            Console.error("we had a problem shutting the mongo daemon down")
            print(e)

    def info(self):
        """
        prints some elementary information about the server
        """
        Console.ok("Mongo parameters")
        if self.dbpath:
            Console.ok("  dbpath:  {:}".format(self.db_path))
        if self.port:
            Console.ok("  port:    {:}".format(self.port))
        if self.log_file:
            Console.ok("  logfile: {:}".format(self.log_file))
        if self.dbname:
            Console.ok("  dbname:  {:}".format(self.dbname))

    def connect(self):
        """
        Creates a connection to the database with the given configuration from the yaml filr
        """

        client = MongoClient('localhost', self.port)
        self.database = client["jobsdb"]
        self.jobs = self.database["jobs"]
        self.id = self.database["id"]  # manages the counter for the job

        if self.info:
           Console.info("Connecting to the Mongo Database")

    def getid(self):
        pass

    def setid(self):
        pass

    def incrid(self):
        pass

    # job-name is unique

    def modify(self, job, overwrite=True):
        """
        job is a dictionary. one of its attributes is 'jobname'.
        The job if it exists will be modified, with attributes
        specified in the dict. If overwrite is True all other
        previously defined attributes are overwritten. if the
        job does not exists it will be added.

        :param job: a new job in dict format
        :param overwrite: if True the element that may already
                          be in teh database will be overwritten.
        :return: returns the id of the job in the database
        """
        matchingJobs = self.find_jobs("job_name", job["job_name"])

        # A job with this job name does not exist
        if matchingJobs.count() == 0:

            # Add a new job
            self.add(job)

        # A job with this job name exists so modify it
        else:

            matchingJob = matchingJobs[0]

            # Overwrite all values
            if overwrite:
                # Clear out the entire dictionary except for ID and job name
                matchingJob.clear()

                # Set the ID and job name of the dictionary to be the same
                matchingJob["_id"] = job["job_name"]
                matchingJob["job_name"] = job["job_name"]

            # Modify all attributes in the dictionary that are not ID or job name
            for key in job:

                if key != "_id" and key != "job_name":
                    matchingJob[key] = job[key]

            self.jobs.save(matchingJob)
            return "todo"  # this should return the database object

    def add(self, job):
        """
        job is a dictionary. one of its attributes is 'job_name'.
        The element is inserted into the db with the id 'job_name'

        :param job: the job to be added
        :return:
        """

        matchingJobs = self.find_jobs("job_name", job["job_name"])

        # A job with this job name already exists
        if matchingJobs.count() != 0:

            Console.error("A job with this job name already exists in the database")

        # A job with this job name does not exist so insert it
        else:

            # Set the ID of this job to be the job name
            job["_id"] = job["job_name"]

            # Set the update time
            update = str(datetime.datetime.now())
            job["update_time"] = update

            # Save the job object
            if self.database is not None:
                db_job_object = self.jobs.save(job)

            return db_job_object

    def add_from_yaml(self, filename):

        #Open and read the YAML file
        file = open(filename, 'r')

        jobDict = yaml.load_all(file)

        #Add every job listed in the YAML file
        for job in jobDict:

            self.add(job)
    
    def insert(self,
               job_name,
               input="",
               output="",
               parameters="",
               job_group=None,
               job_label=None,
               job_id=None,  # possibly same as job_name ?
               host=None,
               start_time=str(datetime.datetime.now()),
               end_time=None,
               update_time=str(datetime.datetime.now()),
               job_status="C_DEFINED",  # see what we wrote in paper
               ):
        """
        inserts a job with specific attributes into the database.

        :param job_name: the name of the job
        :param input: an array of input files
        :param output: an array of output files
        :param parameters: an array of parameters
        :param job_group: the group of the job
        :param job_label: a label for the job
        :param job_id: a unique id for the job
        :param host: the host on which the job is to be run.
        :param start_time: the start time when the job is to be run
        :param end_time: the end time when the job is to be run
        :param update_time: the time the job record has been updated
        :param job_status: the status of the job
        :return: returns the job object
        """

        if self.database is not None:

            job = {
                "_id": job_name,
                "job_name": job_name,
                "job_id": job_name,
                "job_group": job_group,
                "job_label": job_label,
                "job_status": job_status,
                "host": host,
                "input": input,  # must be array
                "output": output,  # must be array
                "start_time": start_time,
                "end_time": end_time,
                "update_time": update_time,
            }

            banner("job")
            pprint(job)
            banner("insert")

            db_job_object = self.jobs.save(job)
            # print (db_job_object)
            # db_job_id = db_job_object
            # print (db_job_id)

            return db_job_object

        else:

            Console.error("Please connect to the database first")
            return -1

    def insert_job_object(self, job):
        """
        insert a job object as defined in job.
        :param job:
        :return:
        """

        if self.database is not None:

            job_id = self.jobs.insert_one(job).inserted_id

            return job_id

        else:
            Console.error("Please connect to the database first")
            return -1

    def check_job_definition(self, jobid):
        """
        checks if the job has all attributes defined
        :param jobid: the id of the job
        :return: None if the job is valid, a list of attributes that
        need to be defined.
        """
        # TODO: needs to be implemented
        pass

    def find_jobs(self, attribute="", value=""):
        """
        finds a job based on if specific attribute has a particular value
        :param attribute: the name of the attribute
        :param value:  the value of the attribute
        :return:
        """

        if self.database is not None:

            # Return all jobs if not given search parameters
            if attribute == "" and value == "":
                return self.jobs.find()

            # Return all jobs given the search parameters
            else:
                return self.jobs.find({attribute: value})

        else:
            Console.error("Please connect to the database first")
            return -1

    def find_jobs_with_file(self, filename):
        """
        filename is the file to be searched for in input and output of all jobs
        :param element:
        :return: two lists are returned where the first is a list of job_names with the given file as input and
                 the second is a list of job_names with the given file as output
        """

        #Empty list of job_names that contain the given file in input an
        matchingInputJobs = []
        matchingOutputJobs = []

        for job in self.find_jobs():

            #Be sure the job has input associated with it
            if "input" in job:

                input = job["input"]

                if filename in input:

                    matchingInputJobs.append(job["job_name"])

            #Be sure the job has output associated with it
            if "output" in job:

                output = job["output"]

                if filename in output:

                    matchingOutputJobs.append(job["job_name"])


        return matchingInputJobs, matchingOutputJobs
    
    def delete(self, jobname):
        """
        delete the job with the given  name
        :param jobname: the name of the jon
        :return:
        """
        self.delete_jobs("job_name", jobname)

    def clear(self):
        """
        clears all jobs from the database
        """
        self.delete_jobs()

    def delete_jobs(self, attribute="", value=""):
        """
        deletes a job where the attribute is set to a specific value
        :param attribute: the attribute name
        :param value: the value
        """
        if self.database is not None:

            # Delete all jobs if no key name or value has been given
            if attribute == "" and value == "":
                self.jobs.remove()

            # Delete only records from a query result if key name and value have been given
            else:
                self.jobs.remove({attribute: value})

        else:
            Console.error("Please connect to the database first")
            return -1

    def __len__(self):
        """
        returns the number of elements in the database
        :return: the number of elements in the database
        """
        return self.count()

    def count(self, attribute="", value=""):
        """
        return the count of all jobs with a given value at the attribute
        :param attribute: the attribute we look at
        :param value: the value the attribute must have
        :return: the cound of objects in the database where attribute == value
        """
        if self.database is not None:

            # Return the count of all jobs if not given search parameters
            if attribute == "" and value == "":
                return self.jobs.count()

            # Return number of results of the query given the search parameters
            else:
                return self.jobs.find(({attribute: value})).count()

        else:
            Console.error("Please connect to the database first")
            return -1

    def update_job_end_time(self, job_id, end_time=str(datetime.datetime.now())):
        """
        updates the job end time
        :param job_id: the job id
        :param end_time: the end time
        :return: returns -1 if not successul
        """
        if self.database is not None:
            self.jobs.update({"_id": job_id}, {"$set": {"end_time": end_time}}, upsert=False)
            return 1
        else:
            Console.error("Please connect to the database first")
            return -1

    def update_job_attribute(self, job_id, attribute, value):
        """
        updates a specific attribute in the database
        :param job_id: the job id
        :param attribute: the attribute
        :param value: the value
        :return: 1 if successful , -1 if error # will be changed to true, false
        """

        if self.database is not None:

            if attribute == "_id":

                print('You cannot change the unique Object ID generated by MongoDB')
                return -1

            else:

                self.jobs.update({"_id": job_id}, {"$set": {attribute: value}}, upsert=False)
                return 1
        else:

            print("Please connect to the database first")
            return -1

    def job_status_stats(self, printOutJobs=False):
        """
        prints the status of all jobs
        :param printOutJobs: if True, prints the detals of the job
        """

        # Array of different job statuses
        # Start with one value for jobs without a status
        jobStatuses = ["No Status"]

        # Parallel array of counts of each job status
        # Start with a counter for jobs with no status
        jobStatusCounts = [0]

        # Loop through all jobs
        for job in self.find_jobs():

            #Job has a status
            if "job_status" in job:

                jobStatusFound = False

                index = 0

                #Loop through all existing job statuses
                for jobStatus in jobStatuses:

                    #Job status match
                    if job["job_status"] == jobStatus:
                        #Increment the counter for this job status
                        jobStatusCounts[index] += 1
                        jobStatusFound = True
                        break

                    index += 1

                #New job status
                if not jobStatusFound:
                    #Add new job status and new counter to arrays
                    jobStatuses.append(job["job_status"])
                    jobStatusCounts.append(1)

            #Job does not have a status
            else:

                #Increment counter
                jobStatusCounts[0] += 1

        index = 0

        #Print out all job statuses and counts
        for jobStatus in jobStatuses:

            #Only print jobs statuses that exist
            if jobStatusCounts[index] != 0:

                print("JOB STATUS: " + jobStatus + " COUNT: " + str(jobStatusCounts[index]))

                #Print out all jobs for this status if flagged to do so
                if printOutJobs:

                    #Loop through all jobs
                    for job in self.find_jobs():

                        #Matching job status
                        if job["job_status"] == jobStatus:
                            print(job)

                    #Print an blank line to make the output more pleasing
                    print("")

            index += 1
    
    def stat(self):
        print("Number of elements: ", self.__len__())

