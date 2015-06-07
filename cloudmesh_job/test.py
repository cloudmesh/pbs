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

db.clear()

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

#Show updating a job attribute
print "\nORIGINAL JOB:"
singleJob = list(db.find_jobs("_id", job1_id))
print singleJob[0]

#Update the input filename
db.update_job_attribute(job1_id, "input_filename", "new_input_file")

#Print out the updated job
print "\nUPDATED JOB:"
singleJob = list(db.find_jobs("_id", job1_id))
print singleJob[0]

#Add a job using add()
job = {"job_name": "job25"}

db.add(job)

#Show modify() functionality
job = {"job_name": "job30", "input_filename":"file1"}

db.modify(job)

print "\nORIGINAL JOB"
for job in db.find_jobs():
    print job

job = {"job_name": "job30", "input_filename":"file2"}

db.modify(job)

print "MODIFIED JOB"
for job in db.find_jobs():
    print job

#Show job statuses functionality
print "\nJOB STATUSES:"
db.job_status_stats()

print "\nJOB STATUSES WITH JOBS PRINTED:"
db.job_status_stats(True)

#SHOW FIND_JOBS_WITH_FILE
job100_id = db.insert("job100")
job101_id = db.insert("job101", "file100", "file200")
job102_id = db.insert("job102", "file200", "file300")

inputs, outputs = db.find_jobs_with_file("file200")

print("\nJobs with matching file in input:")
for job in inputs:
    print job

print("\nJobs with matching file in output:")
for job in outputs:
    print job
    
#Delete all jobs
db.clear()
    
#SHOW ADD_FROM_YAML
db.add_from_yaml("job_example.yaml")

for job in db.find_jobs():
    print job

#Delete all jobs
db.clear()
print "Database cleared."
print "Job count: " + str(db.count())

db.stop()
