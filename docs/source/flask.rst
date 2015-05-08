Develop an informational REST service that uses the OpenPBS class. The routs are as follows

Informational routes

/pbs/
/pbs/job/id/<id>
/pbs/job/user/<user>
/pbs/queue/name/<name>


You will be using

https://flask-restful.readthedocs.org/en/0.3.2/index.html

see

https://flask-restful.readthedocs.org/en/0.3.2/quickstart.html#full-example

you would develop the classes


from flask import Flask
from flask.ext.restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)


class JobList

   def get(self):
       "gets all jobs"

   def post(self):
       "gets a job with a particular id that you post"

class QueueList

   def get(self):
       "gets all jobs"

   def post(self):
       "gets a queue with a particular name that you post"

api.add_resource(JobList, '/pbs/job/<id>')
api.add_resource(QueueList, '/pbs/queue/<id>')
...



