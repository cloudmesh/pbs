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
        self.data = ConfigDict(filename=self.filename)

        self.port = self.data["cloudmesh"]["jobdatabase"]["port"]
        self.log_file = self.data["cloudmesh"]["jobdatabase"]["log"]
        self.db_file = self.data["cloudmesh"]["jobdatabase"]["filename"]
        self.job_dir = os.path.dirname(self.db_file)

    def __init__(self, deploy=True, yaml_filename="/cloudmesh_pbs.yaml"):
        """
        Creates an object instance of a job database as defined in the cloudmesh_pbs yaml file

        :param deploy: If True, creates the configuration files
        :param yaml_filename: The cloudmesh pbs yaml file. Defaults to
                              cloudmesh_pbs.yaml
        :return: an object for manageing jobs in the database
        """
        self.load(filename=yaml_filename)

        if deploy:
            self._deploy()

    def _deploy(self):
        """
        creates the directories if they do not exist
        :return:
        """
        try:
            for file in [self.db_file, self.log_file]:
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
                               "--dbpath", self.db_file,
                               "--port", self.port,
                               "--fork",
                               "--logpath", self.log_file)

        except Exception, e:
            Console.error("we had a problem starting the  mongo daemon")
            print(e)

        Console.ok("MongoDB has stopped")

        Console.ok("MongoDB has been deployed at path {:} on port {:} with log {:}"
                   .format(db_file, port, log_file))

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
        Console.ok("  dbpath:", self.db_file)
        Console.ok("  port:", self.port)
        Console.ok("  port:", self.log_file)

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

