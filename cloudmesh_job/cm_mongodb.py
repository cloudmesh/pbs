# TODO instead of using subprocess, we like to use cloudmesh_base.Shell
import subprocess
from cloudmesh_base.Shell import _execute
from cloudmesh_base.Shell import mkdir
from cloudmesh_base.tables import dict_printer
from cloudmesh_base.Shell import Shell
from cloudmesh_base.util import banner
from cloudmesh_base.util import path_expand

import pymongo
from pymongo import MongoClient
import datetime

class job_db (object):


    database = None
    jobs = None

    def __init__(self, deploy=True, yaml_filename="/cloudmesh_pbs.yaml"):
        """
        Creates an object instance of a job database as defined in the cloudmesh_pbs yaml file

        :param deploy: If True, creates the configuration files
        :param yaml_filename: The cloudmesh pbs yaml file. Defaults to
                              cloudmesh_pbs.yaml
        :return: an object for manageing jobs in the database
        """
        self.yaml_filename = config_file(yaml_filename)

        self.pbs_dir = config_file("/pbs")
        self.id_file = config_file("/pbs/id.txt")
        self.db_file = config_file("/pbs/job.db")

        if deploy:
            self.deploy()
        self.load()
        self.id = self.jobid

        self.pbs_nodes_data = None

    # BUG not a good location for  the data /data
    # BUG not a good location for logpath as we run this in user mode
    def startMongo(self, db_path="/data/db/", port="27017", log_path="/var/log/mongod"):

        #Create the data path and log path in case they do not exist
        Shell.mkdir(db_path)
        Shell.mkdir(log_path)

        #Deploy the mongoDB
        # use Shell
        r = Shell._execute("mongod", "--dbpath", db_path, "--port", port, "--fork", "--logpath", log_path)

        print "MongoDB has been deployed at path " + db_path + " on port " + port + " with log " + log_path

    def stopMongo(self):

        r = Shell.execute("mongod", "--shutdown")

        print "MongoDB has stopped"

    def connect(self, db_name):

        client = MongoClient()

        self.database = client[db_name]
        self.jobs = self.database.jobs

    def insertJob(self,
                  job_name,
                  job_group,
                  job_label,
                  job_status="C_DEFINED",  # see what we wrote in paper
                  job_id,     # possibly same as job_name ?
                  input_filename="",
                  output_filename="",
                  start_time=str(datetime.datetime.now()),
                  end_time=str(datetime.datetime.now())):
                # TODO: end_teme should be None as unlikely
                # it so short and we need to deal with jobs
                # that we do not know how long they are

        if self.database is not None:

            job = {"job_name"        : job_name,
                   "job_id"          : job_name,
                   "job_group"       : job_group,
                   "job_label"       : job_label,
                   "job_status"      : job_status,
                   "input_filename"  : input_filename, # must be array
                   "output_filename" : output_filename, # must be array
                   "start_time"      : start_time,
                   "end_time"        : end_time
                   }

            job_id = self.jobs.insert_one(job).inserted_id

            return job_id

        else:

            print "Please connect to a cloudmesh_job before running this function"
            return -1

    def insertJobObject(self, job):

        if self.database is not None:

            job_id = self.jobs.insert_one(job).inserted_id

            return job_id

        else:

            print "Please connect to a cloudmesh_job before running this function"
            return -1

    def findJobs(self, key_name="", value=""):

        if self.database is not None:

            #Return all jobs if not given search parameters
            if key_name == "" and value == "":
                return self.jobs.find()

            #Return all jobs given the search parameters
            else:
                return self.jobs.find({key_name: value})

        else:

            print "Please connect to a cloudmesh_job before running this function"
            return -1

    def deleteJobs(self, key_name="", value=""):

        if self.database is not None:

            #Delete all jobs if no key name or value has been given
            if key_name == "" and value == "":
                self.jobs.remove()

            #Delete only records from a query result if key name and value have been given
            else:
                self.jobs.remove({key_name: value})

        else:

            print "Please connect to a cloudmesh_job before running this function"
            return -1

    def numJobs(self, key_name="", value=""):

        if self.database is not None:

            #Return the count of all jobs if not given search parameters
            if key_name == "" and value == "":
                return self.jobs.count()

            #Return number of results of the query given the search parameters
            else:
                return self.jobs.find(({key_name: value})).count()

        else:

            print "Please connect to a cloudmesh_job before running this function"
            return -1

    def updateJobEndTime(self, job_id, end_time=str(datetime.datetime.now())):

        if self.database is not None:

            self.jobs.update({"_id" : job_id}, {"$set": {"end_time" : end_time}}, upsert=False)

        else:

            print "Please connect to a cloudmesh_job before running this function"
            return -1

    # TODO: not needed as implemented in cloudmesh_base
    # Create a directory and all of its sub directories
    # def createPath(self, completePath, lastPathIsADirectory):
    #
    #    #Split the full path on all slashes
    #   paths = completePath.split("/")
    #
    #    #Build the string of the base directory and all sub directories to the current one
    #    currentPath = ""
    #
    #    index = 0
    #
    #    #Loop through all paths
    #    for path in paths:
    #
    #        #Path is blank so do not create a directory
    #        if path == "":
    #
    #            #Current path is not the last path
    #            if index != len(paths) - 1:
    #
    #               #Add a slash
    #               currentPath = currentPath + "/"
    #
    #        #Path exists, create the path and add it to the string tracking the complete path
    #        else:
    #
    #            #Current path is the last path
    #            if index == len(paths) - 1:
    #
    #                #Do not add a slash on the end
    #                currentPath = currentPath + path
    #
    #            else:
    #                currentPath = currentPath + path + "/"
    #
    #            #Only create the directory if the current path is not the last path or
    #            #   the path is the last path and it has been flagged as a directory
    #            if index != len(paths) - 1 or (index == len(paths) - 1 and lastPathIsADirectory):
    #
    #                #Attempt to create the directories
    #                try:
    #                    error = subprocess.call(["mkdir", currentPath])
    #
    #                except:
    #                    print "The directory " + currentPath + " already exists"
    #
    #        index += 1
