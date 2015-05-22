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

class JobDB(object):

    database = None
    jobs = None

    def isup(self):
        """
        returns True is mongod is up

        TODO: implement
        :return:
        """
        return True

    def load(self, filename="/cloudmesh_pbs.yaml"):
        self.filename = config_file(filename)
        self.data = ConfigDict(filename=self.filename)

        self.port = self.data["cloudmesh"]["jobdatabase"]["port"]
        self.db_path = path_expand(self.data["cloudmesh"]["jobdatabase"]["db_path"])
        self.log_file = path_expand(self.db_path + "/dbjobs.log")
        self.dbname = self.data["cloudmesh"]["jobdatabase"]["dbname"]

    def __init__(self, yaml_filename="/cloudmesh_pbs.yaml"):
        """
        Creates an object instance of a job database as defined in the cloudmesh_pbs yaml file

        :param deploy: If True, creates the configuration files
        :param yaml_filename: The cloudmesh pbs yaml file. Defaults to
                              cloudmesh_pbs.yaml
        :return: an object for manageing jobs in the database
        """
        self.load(filename=yaml_filename)
        self.deploy()

    def deploy(self):
        """
        creates the directories if they do not exist
        :return:
        """
        banner("CREATE DIRS")
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
        r = Shell.fgrep(Shell.ps("aux", _tty_out=False), "mongod", _tty_in=False)
        print(r)

    def start(self):
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
            #a = subprocess.call(command)
            os.system(" ".join(command))
            os.system ("ps aux | fgrep mongod")
            Console.ok("MongoDB has been deployed")
            self.info()

        except Exception, e:
            Console.error("we had a problem starting the  mongo daemon")
            print(e)
            Console.error("MongoDB has stopped")
            # TODO remove the exit in final code, for debugging only
            sys.exit()


    def stop(self):
        try:
            #command = ["mongod", "--shutdown"]
            command = ["killall", "mongod"]
            print(" ".join(command))
            os.system(" ".join(command))
            Console.ok("MongoDB has been shutdown")
            #os.system("mongod --shutdown")
        except Exception, e:
            Console.error("we had a problem shutting the mongo daemon down")
            print(e)


    def info(self):
        # TODO: implement self. dbath, self.port, self.logpath
        Console.ok("Mongo parameters")
        Console.ok("  dbpath:  {:}".format(self.db_path))
        Console.ok("  port:    {:}".format(self.port))
        Console.ok("  logfile: {:}".format(self.log_file))
        Console.ok("  dbname:  {:}".format(self.dbname))

    def connect(self):

        client = MongoClient('localhost', self.port)
        self.database = client["jobsdb"]
        self.jobs = self.database["jobs"]
        self.id = self.database["id"]  # manages the counter for the job

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

        :param element:
        :return:
        """
        print("TODO: Ryan")

    def add(self, job):
        """
        job is a dictionary. one of its attributes is 'jobname'.
        The element is inserted into the db with the id 'jobname'

        :param element:
        :return:
        """
        print("TODO: Ryan")

        # TODO: check if jobname exists and print error if it does.

        update = str(datetime.datetime.now())
        job["update_time"] = update
        print("not yet implemented")
        if self.database is not None:
            db_job_object = self.jobs.save(job)

        return db_job_object

    def insert(self,
               job_name,
               input_filename="",
               output_filename="",
               parameters="",
               job_group=None,
               job_label=None,
               job_id=None,  # possibly same as job_name ?
               host=None,
               start_time=str(datetime.datetime.now()),
               end_time=str(datetime.datetime.now()),
               update_time=str(datetime.datetime.now()),
               job_status="C_DEFINED",  # see what we wrote in paper
):
        # TODO: end_time should be None as unlikely
        # it so short and we need to deal with jobs
        # that we do not know how long they are

        if self.database is not None:

            job = {
                   "_id": job_name,
                   "job_name": job_name,
                   "job_id": job_name,
                   "job_group": job_group,
                   "job_label": job_label,
                   "job_status": job_status,
                   "host": host,
                   "input_filename": input_filename,  # must be array
                   "output_filename": output_filename,  # must be array
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

        if self.database is not None:

            job_id = self.jobs.insert_one(job).inserted_id

            return job_id

        else:
            Console.error("Please connect to the database first")
            return -1

    def find_jobs(self, attribute="", value=""):

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

    def delete(self, jobname):
        self.delete_jobs(attribute='name', value=jobname)

    def delete_jobs(self, attribute="", value=""):

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
        returns the number of elemenst in the database
        :return:
        """
        return self.count()

    def count(self, attribute="", value=""):
        """
        return the count of all jobs with a given value at the attribute
        :param attribute:
        :param value:
        :return:
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

        if self.database is not None:

            self.jobs.update({"_id": job_id}, {"$set": {"end_time": end_time}}, upsert=False)

        else:
            Console.error("Please connect to the database first")
            return -1
            
    def updateJobAttribute(self, job_id, attribute, value):

        if self.database is not None:

            if attribute == "_id":

                print ('You cannot change the unique Object ID generated by MongoDB')

            else:

                self.jobs.update({"_id" : job_id}, {"$set": {attribute : value}}, upsert=False)

        else:

            print ("Please connect to the database first")
            return -1   
            
    def jobStatusStats(self, printOutJobs=False):

        #Array of different job statuses
        jobStatuses = []

        #Parallel array of counts of each job status
        jobStatusCounts = []

        #Loop through all jobs
        for job in self.findJobs():

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
            if jobStatusFound == False:

                #Add new job status and new counter to arrays
                jobStatuses.append(job["job_status"])
                jobStatusCounts.append(1)

        index = 0

        #Print out all job statuses and counts
        for jobStatus in jobStatuses:

            print ("JOB STATUS: " + jobStatus + " COUNT: " + str(jobStatusCounts[index]))

            #Print out all jobs for this status if flagged to do so
            if printOutJobs:

                #Loop through all jobs
                for job in self.findJobs():

                    #Matching job status
                    if job["job_status"] == jobStatus:

                        print (job)

                #Print an blank line to make the output more pleasing
                print ("")

            index += 1
    

