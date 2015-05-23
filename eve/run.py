#
# how to test
#
#  python eve/run.py     in one terminal
#
#  curl -i http://localhost:5000/jobs
#
#

from flask.ext.bootstrap import Bootstrap
from eve_docs import eve_docs
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
Bootstrap(app)
app.register_blueprint(eve_docs, url_prefix='/docs')

if __name__ == '__main__':
    app.run()


