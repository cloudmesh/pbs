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
import time


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

    def wait(self, max_wait_time=60, delta=5):
        """
        waits til the server is up
        :return:
        """
        for i in range(0, max_wait_time, delta):
            if self.isup():
                return
            time.sleep(5)
        raise Exception("server not up")

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

    def __init__(self,
                 filename="/cloudmesh_pbs.yaml",
                 debug=False):
        """
        Creates an object instance of a job database as defined in the cloudmesh_pbs yaml file

        :param deploy: If True, creates the configuration files
        :param yaml_filename: The cloudmesh pbs yaml file. Defaults to
                              cloudmesh_pbs.yaml
        :return: an object for manageing jobs in the database
        """
        self.load(filename=filename)
        self.deploy()
        self.debug = debug

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
        try:
            process_id = self.pid()
            command = ["kill", "-9", str(process_id)]
            print(" ".join(command))
            os.system(" ".join(command))
            Console.ok("MongoDB has been shutdown")
        except Exception, e:
            Console.error("we had a problem shutting the mongo daemon down")
            print(e)

    def info(self):
        """
        prints some elementary information about the server
        """
        Console.ok("Mongo parameters")
        if self.db_path:
            Console.ok("  dbpath:  {:}".format(self.db_path))
        if self.port:
            Console.ok("  port:    {:}".format(self.port))
        if self.log_file:
            Console.ok("  logfile: {:}".format(self.log_file))
        if self.dbname:
            Console.ok("  dbname:  {:}".format(self.dbname))
        try:
            Console.ok("  pid:     {:}".format(self.pid()))
        except:
            pass
        try:
            db = self.connect()
            Console.ok("  Objects: {:}".format(len(db)))
        except:
            pass

    def connect(self):
        """
        Creates a connection to the database with the given configuration
        from the yaml file
        """

        client = MongoClient('localhost', self.port)
        self.database = client["jobsdb"]
        self.jobid = self.database["jobsid"]
        self.jobs = self.database["jobs"]
        self.jobscripts = self.database["jobscripts"]
        self.id = self.database["id"]  # manages the counter for the job

        if self.debug:
            Console.info("Connecting to the Mongo Database")

    def add_from_yaml(self, filename):
        """
        adds jobs of the following form to the database

        ::

            job2:
                program: myprg
                parameters: -a -l
                input:
                - in1.txt
                - in2.txt
                output:
                - out1.txt
                - out2.txt
                group: experiment1
                label: job2
                host: None
                start: +2h

        :param filename: the yaml filename
        """
        d = None
        print(filename)
        stream = file(path_expand(filename), 'r')
        # if f does not exists error
        try:
            jobs = yaml.load(stream)
        except Exception, e:
            print("ERROR: loading file", filename)
            print(e)
            return

        for name in jobs:
            job = jobs[name]
            job['job_name'] = name
            pprint(job)
            try:
                self.add(job)
            except Exception, e:
                print("ERROR: adding", name)
                print(e)
        return

    def get_jobid(self):
        """returns the next job id"""
        result = {'value': 0}
        try:
            result = self.jobid.find({'_id': 'jobid'})[0]
        except:
            pass
        return int(result['value'])

    def set_jobid(self, value):
        """sets the current job id to the given value"""
        # delete the id

        id_dict = {'_id': 'jobid', 'value': int(value)}

        self.jobid.save(id_dict)

    def incr_jobid(self):
        """increments the job id"""
        job_id = self.get_jobid()
        job_id = job_id + 1
        self.set_jobid(job_id)

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

    def add_script(self, name, script):
        """
        uploads the script with the given name

        :param name: name of the script
        :param script: the script text
        """
        id_dict = {'_id': name, 'script': script}
        self.jobscripts.save(id_dict)

    def add_script_from_file(self, name, filename):
        """
        uploads the script with the given name

        :param name: name of the script
        :param filename: the script file
        :return:
        """
        with open (filename, "r") as f:
            data = f.read()
        self.add_script(name, data)

    def write_script(self, name, filename):
        print("Writing script", name, "to", filename)
        data = self.get_script(name)
        with open (filename, "w") as f:
            f.write(data)

    def get_script(self, name):
        """
        returns the script with the given name

        :param name: The name of the script
        :return: The script as a String
        """
        script = self.jobscripts.find(({"_id": name}))[0]['script']
        return script

    def list_scripts(self):
        script_names = []
        cursor = self.jobscripts.find()
        for script in cursor:
            name= script["_id"]
            script_names.append(name)
        if script_names == []:
            return None
        else:
            return script_names

    def delete_script(self, name):
        if "all" == name:
            self.jobscripts.remove({})
        else:
            self.jobscripts.remove({"_id": name})

    def add(self, job):
        """
        job is a dictionary. One of its attributes is 'name'.
        The element is inserted into the db with the id 'name'

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

    def insert(self,
               job_name,
               input="",
               output="",
               program="",
               parameters="",
               job_group=None,
               job_label=None,
               job_id=None,  # possibly same as name ?
               host=None,
               start_time=str(datetime.datetime.now()),
               end_time=None,
               update_time=str(datetime.datetime.now()),
               job_status="C_DEFINED",  # see what we wrote in paper
               ):
        """
        inserts a job with specific attributes into the database.

        :param name: the name of the job
        :param input: an array of input files
        :param output: an array of output files
        :param program: the executable
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
                "program": program,
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

            banner("insert job", c=".")
            pprint(job)

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
        :return: two lists are returned where the first is a list of job names with the given file as input and
                 the second is a list of job names with the given file as output
        """

        # Empty list of job names that contain the given file in input an
        matchingInputJobs = []
        matchingOutputJobs = []

        for job in self.find_jobs():

            # Be sure the job has input associated with it
            if "input" in job:

                input = job["input"]

                if filename in input:
                    matchingInputJobs.append(job["job_name"])

            # Be sure the job has output associated with it
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

            # Job has a status
            if "job_status" in job:

                jobStatusFound = False

                index = 0

                # Loop through all existing job statuses
                for jobStatus in jobStatuses:

                    # Job status match
                    if job["job_status"] == jobStatus:
                        # Increment the counter for this job status
                        jobStatusCounts[index] += 1
                        jobStatusFound = True
                        break

                    index += 1

                # New job status
                if not jobStatusFound:
                    # Add new job status and new counter to arrays
                    jobStatuses.append(job["job_status"])
                    jobStatusCounts.append(1)

            # Job does not have a status
            else:

                # Increment counter
                jobStatusCounts[0] += 1

        index = 0

        # Print out all job statuses and counts
        for jobStatus in jobStatuses:

            # Only print jobs statuses that exist
            if jobStatusCounts[index] != 0:

                print("JOB STATUS: " + jobStatus + " COUNT: " + str(jobStatusCounts[index]))

                # Print out all jobs for this status if flagged to do so
                if printOutJobs:

                    # Loop through all jobs
                    for job in self.find_jobs():

                        # Matching job status
                        if job["job_status"] == jobStatus:
                            print(job)

                    # Print an blank line to make the output more pleasing
                    print("")

            index += 1

    def stat(self):
        print("Number of elements: ", self.__len__())

