#
# how to test
#
#  python eve/run.py     in one terminal
#
#  curl -i http://localhost:5000/jobs
#
#


from cloudmesh_job.cm_jobdb import JobDB

db = JobDB()

print db.port

my_settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': db.port,
    'MONGO_DBNAME': 'jobsdb',
    'DOMAIN': {'jobs': {}}
}

from eve import Eve
app = Eve(settings=my_settings)

if __name__ == '__main__':
    app.run()

