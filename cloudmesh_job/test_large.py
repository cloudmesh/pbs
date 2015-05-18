import cm_mongodb

db = cm_mongodb.db()

db.startMongo()

#Connect to test cloudmesh_job
print "Connecting to local cloudmesh_job"

db.connect("newdb")

#Insert 20 jobs
#   Use different job names but identical input and output filenames for later queries
print "\nInserting all jobs"

for i in range(0, 20):
    db.insertJob("job" + str(i), "input", "output")

#Print out all jobs
print "\nAll Jobs:"

for job in db.findJobs():
    print job

#Print all jobs with job name as "job2"
#Available key names at this time are:
#   _id
#   job_name
#   input_filename
#   output_filename
print "\nJob with Job Name as 'job2'"

for job in db.findJobs("job_name", "job2"):
    print job

#Print out count of all jobs
numJobs = db.numJobs()
print "\nNumber of Total Jobs: " + str(numJobs)

#Print out count of all jobs with job name as "job2"
numJobs2 = db.numJobs("job_name", "job2")
print "\nNumber of Jobs with Job Name as 'job2': " + str(numJobs2)

#Delete all jobs with job name as "job2"
db.deleteJobs("job_name", "job2")

#Print out count of all jobs with job name as "job2"
print "\nDeleting all jobs with job name as 'job2'"

numJobs2 = db.numJobs("job_name", "job2")
print "Number of Jobs with Job Name as 'job2': " + str(numJobs2)

#Delete all jobs
db.deleteJobs()

#Print out count of all jobs
print "\nDeleting all remaining jobs"
numJobs = db.numJobs()
print "Number of Total Jobs: " + str(numJobs)