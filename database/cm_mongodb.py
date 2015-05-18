# TODO instead of using subprocess, we like to use cloudmesh_base.Shell
import subprocess
import pymongo
from pymongo import MongoClient
import datetime

class db:

    database = None
    jobs = None

    # BUG not a good location for  the data /data
    # BUG not a good location for logpath as we run thi sin user mode
    def startMongo(self, db_path="/data/db/", port="27017", log_path="/var/log/mongod"):

        #Create the data path in case it does not already exist
        subprocess.call(["mkdir", "/data"])
        # try:
        #   r = Shell.mkdir("/data")
        # except:
        #   print " could not cretae"
        # BUG / is not a good location for data and will not work on some systems
        subprocess.call(["mkdir", db_path])

        #Deploy the mongoDB
        # use Shell
        subprocess.call(["mongod", "--dbpath", db_path, "--port", port, "--fork", "--logpath", log_path])

        print "MongoDB has been deployed at path " + db_path + " on port " + port + " with log " + log_path

    def stopMongo(self):

        subprocess.call(["mongod", "--shutdown"])

        print "MongoDB has stopped"

    def connect(self, db_name):

        client = MongoClient()

        self.database = client[db_name]
        self.jobs = self.database.jobs

    def insertJob(self, job_name, input_filename="", output_filename="", start_time=str(datetime.datetime.now()), end_time=str(datetime.datetime.now())):

        if self.database is not None:

            job = {"job_name"        : job_name,
                   "input_filename"  : input_filename,
                   "output_filename" : output_filename,
                   "start_time"      : start_time,
                   "end_time"        : end_time
                   }

            job_id = self.jobs.insert_one(job).inserted_id

            return job_id

        else:

            print "Please connect to a database before running this function"
            return -1

    def insertJobObject(self, job):

        if self.database is not None:

            job_id = self.jobs.insert_one(job).inserted_id

            return job_id

        else:

            print "Please connect to a database before running this function"
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

            print "Please connect to a database before running this function"
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

            print "Please connect to a database before running this function"
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

            print "Please connect to a database before running this function"
            return -1

    def updateJobEndTime(self, job_id, end_time=str(datetime.datetime.now())):

        if self.database is not None:

            self.jobs.update({"_id" : job_id}, {"$set": {"end_time" : end_time}}, upsert=False)

        else:

            print "Please connect to a database before running this function"
            return -1