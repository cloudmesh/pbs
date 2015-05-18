import cm_mongodb

db = cm_mongodb.db()

db.startMongo()

#Connect to cloudmesh_job
db.connect("test")

#Insert two jobs - one with only a name and one with input and output files
job0_id = db.insertJob("job0")
job1_id = db.insertJob("job1", "input1", "output1")

#Print job IDs of both added jobs
print job0_id
print job1_id

#Get all jobs with given parameters
#Available key names at this time are:
#   _id
#   job_name
#   input_filename
#   output_filename
jobs = db.findJobs("job_name", "job1")

#Print out all returned jobs
for job in jobs:
    print job

#Query by job ID to return a single job
singleJob = db.findJobs("_id", job0_id)

#Print out the first job in the list
print singleJob[0]

#Print out count of all jobs
print db.numJobs()

#Print out count of jobs given query parameters
print db.numJobs("job_name", "job1")

db.stopMongo()