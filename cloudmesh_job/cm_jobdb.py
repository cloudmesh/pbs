from __future__ import print_function

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


class JobDB(object):
    database = None
    jobs = None

    def load(self, filename="/cloudmesh_pbs.yaml"):
        self.filename = config_file(filename)
        self.data = ConfigDict(filename=filename)

        self.port = self.data["cloudmesh"]["jobdatabase"]["port"]
        self.log_file = self.data["cloudmesh"]["jobdatabase"]["log"]
        self.db_file = self.data["cloudmesh"]["jobdatabase"]["filename"]

    def __init__(self, deploy=True, yaml_filename="/cloudmesh_pbs.yaml"):
        """
        Creates an object instance of a job database as defined in the cloudmesh_pbs yaml file

        :param deploy: If True, creates the configuration files
        :param yaml_filename: The cloudmesh pbs yaml file. Defaults to
                              cloudmesh_pbs.yaml
        :return: an object for manageing jobs in the database
        """

        self.id_file = config_file("/pbs/id.txt")
        self.db_file = config_file("/pbs/job.db")
        self.job_dir = os.path.dirname(self.db_file)

        self.load(filename=yaml_filename)

        if deploy:
            self._deploy()

    def _deploy(self):
        """
        creates the directories if they do not exist
        :return:
        """
        try:
            for file in [self.db_path, self.log_path]:
                r = Shell.mkdir(os.path.dirname(file))
        except Exception, e:
            Console.error("Problem creationg the database directory")
            print(e)

    # TODO COMBINE WITH __INIT__ ???
    # BUG not a good location for  the data /data
    # BUG not a good location for logpath as we run this in user mode
    # port and location should probably read from cloudmesh_pbs.yaml and values here set to None.see load function

    def start(self):
        try:
            r = Shell._execute("mongod",
                               "--dbpath", self.db_path,
                               "--port", self.port,
                               "--fork",
                               "--logpath", self.log_path)

        except Exception, e:
            Console.error("we had a problem starting the  mongo daemon")
            print(e)

        Console.ok("MongoDB has stopped")

        Console.ok("MongoDB has been deployed at path {:} on port {:} with log {:}"
                   .format(db_path, port, log_path))

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

    def insert(self,
               host,
               job_name,
               job_group,
               job_label,
               job_id,  # possibly same as job_name ?
               input_filename="",
               output_filename="",
               start_time=str(datetime.datetime.now()),
               end_time=str(datetime.datetime.now()),
               update_time=str(datetime.datetime.now()),
               job_status="C_DEFINED",  # see what we wrote in paper
):
        # TODO: end_teme should be None as unlikely
        # it so short and we need to deal with jobs
        # that we do not know how long they are

        if self.database is not None:

            job = {"job_name": job_name,
                   "job_id": job_name,
                   "job_group": job_group,
                   "job_label": job_label,
                   "job_status": job_status,
                   "input_filename": input_filename,  # must be array
                   "output_filename": output_filename,  # must be array
                   "start_time": start_time,
                   "end_time": end_time
                   }

            job_id = self.jobs.insert_one(job).inserted_id

            return job_id

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

            # TODO: not needed as implemented in cloudmesh_base
            # Create a directory and all of its sub directories
            # def createPath(self, completePath, lastPathIsADirectory):
            #
            # #Split the full path on all slashes
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
