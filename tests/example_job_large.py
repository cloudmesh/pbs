#
# run with
#
# rm -rf ~/.cloudmesh/pbs/db/; killall mongod; python setup.py install; python cloudmesh_job/example_job_large.py
import cm_jobdb

def main():

    db = cm_jobdb.JobDB()

    db.start()

    # Connect to test cloudmesh_job
    print "Connecting to local cloudmesh_job"

    db.connect()

    # Insert 20 jobs
    # Use different job names but identical input and output filenames for later queries
    print "\nInserting all jobs"

    for i in range(0, 20):
        db.insert("job" + str(i), "input", "output")

    # Print out all jobs
    print "\nAll Jobs:"

    for job in db.find_jobs():
        print job

    # Print all jobs with job name as "job2"
    # Available key names at this time are:
    #   _id
    #   job_name
    #   input_filename
    #   output_filename
    print "\nJob with Job Name as 'job2'"

    for job in db.find_jobs("job_name", "job2"):
        print job

    # Print out count of all jobs
    numJobs = db.count()
    print "\nNumber of Total Jobs: " + str(numJobs)

    # Print out count of all jobs with job name as "job2"
    numJobs2 = db.count("job_name", "job2")
    print "\nNumber of Jobs with Job Name as 'job2': " + str(numJobs2)

    # Delete all jobs with job name as "job2"
    db.delete_jobs("job_name", "job2")

    # Print out count of all jobs with job name as "job2"
    print "\nDeleting all jobs with job name as 'job2'"

    numJobs2 = db.count("job_name", "job2")
    print "Number of Jobs with Job Name as 'job2': " + str(numJobs2)

    # Delete all jobs
    db.delete_jobs()

    # Print out count of all jobs
    print "\nDeleting all remaining jobs"
    numJobs = db.count()
    print "Number of Total Jobs: " + str(numJobs)


if __name__ == "__main__":
    main()