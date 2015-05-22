#
# use as follows
# cd to the cloudmesh_pbs dir
# rm -rf ~/.cloudmesh/pbs/db/; killall mongod; python setup.py install; python cloudmesh_job/test.py
#

from cloudmesh_job.cm_jobdb import JobDB
from cloudmesh_base.util import banner
from bson.objectid import ObjectId

db = JobDB()

banner("info")
db.info()

db.start()

# db.ps()


db.connect()

#Insert two jobs - one with only a name and one with input and output files
job0_id = db.insert("job0")
job1_id = db.insert("job1", "input1", "output1")

#Print job IDs of both added jobs
print job0_id
print job1_id

#Get all jobs with given parameters
#Available key names at this time are:
#   _id
#   job_name
#   input_filename
#   output_filename
jobs = db.find_jobs("job_name", "job1")

#Print out all returned jobs
for job in jobs:
    print job

#Query by job ID to return a single job
singleJob = list(db.find_jobs("_id", job0_id))

#Print out the first job in the list
print singleJob[0]

#Print out count of all jobs
print db.count()

#Print out count of jobs given query parameters
print db.count("job_name", "job1")

#Show updating a job attribute - note this is untested
print "\nORIGINAL JOB:"
singleJob = list(db.find_jobs("_id", job1_id))
print singleJob[0]

#Update the input filename
db.updateJobAttribute(job1_id, "input_filename", "new_input_file")

#Print out the updated job
print "\nUPDATED JOB:"
singleJob = list(db.find_jobs("_id", job1_id))
print singleJob[0]

db.stop()
