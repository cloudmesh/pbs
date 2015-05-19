from __future__ import print_function

from cloudmesh_base.Shell import _execute
from cloudmesh_base.Shell import mkdir
from cloudmesh_base.tables import dict_printer
from cloudmesh_base.Shell import Shell
from cloudmesh_base.util import banner
from cloudmesh_base.util import path_expand
from cmd3.console import Console

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

        ## TODO see DbPBS
        # if deploy:
        #    self.deploy()
        #self.load()
        #self.id = self.jobid

        #self.pbs_nodes_data = None

    # TODO COMBINE WITH __INIT__ ???
    # BUG not a good location for  the data /data
    # BUG not a good location for logpath as we run this in user mode
    def start(self,
              db_path="/pbs/",  # will be in ~/.cloudmesh/pbs
              port="27018",  # will be in ~/.cloudmesh/pbs/lob
              log_path="/pbs/log/"):

        #Create the data path and log path in case they do not exist
        Shell.mkdir(db_path)
        Shell.mkdir(log_path)

        #Deploy the mongoDB
        # use Shell
        try:

            r = Shell._execute("mongod",
                               "--dbpath", db_path,
                               "--port", port,
                               "--fork",
                               "--logpath", log_path)

        except Exception, e:
            Console.error("we had a problem starting the  mongo daemon")
            print(e)

        Console.ok("MongoDB has stopped")

        Console.ok("MongoDB has been deployed at path {:} on port {:} with log {:}".format(db_path, port, log_path))

    def stop(self):
        try:
            r = Shell.execute("mongod", "--shutdown")
        except Exception, e:
            Console.error("we had a problem shutting the mongo daemon down")
            print(e)

        Console.ok("MongoDB has stopped")

    def info(self):
        # TODO: implement self. dbath, self.port, self.logpath
        Console.ok("Mongo parameters")
        Console.ok("  dbpath:", self.dbpath)
        Console.ok("  port:", self.port)
        Console.ok("  port:", self.logpath)

    def connect(self, db_name):

        client = MongoClient()

        self.database = client[db_name]
        self.jobs = self.database.jobs

        Console.info("Connecting to the Mongo Database")

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

            Console.error("Please connect to the database first")
            return -1

    def insertJobObject(self, job):

        if self.database is not None:

            job_id = self.jobs.insert_one(job).inserted_id

            return job_id

        else:
            Console.error("Please connect to the database first")
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
            Console.error("Please connect to the database first")
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
            Console.error("Please connect to the database first")
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
            Console.error("Please connect to the database first")
            return -1

    def updateJobEndTime(self, job_id, end_time=str(datetime.datetime.now())):

        if self.database is not None:

            self.jobs.update({"_id" : job_id}, {"$set": {"end_time" : end_time}}, upsert=False)

        else:
            Console.error("Please connect to the database first")
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
