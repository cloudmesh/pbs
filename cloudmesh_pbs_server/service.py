from flask import Flask
from flask.ext import restful
from flask_restful_swagger import swagger

app = Flask(__name__)
api = restful.Api(app)

# https://flask-restful.readthedocs.org/en/0.3.2/quickstart.html#a-minimal-api

# Develop an informational REST service that uses the OpenPBS
# class. The routs are as follows

# Informational routes

#/pbs/
#/pbs/job/id/<id>
#/pbs/job/user/<user>
#/pbs/queue/name/<name>


#You will be using

#https://flask-restful.readthedocs.org/en/0.3.2/index.html

#see

#https://flask-restful.readthedocs.org/en/0.3.2/quickstart.html#full-example


from flask import Flask
from flask.ext.restful import reqparse, abort, Api, Resource

from cloudmesh_pbs.OpenPBS import OpenPBS

app = Flask(__name__)
api = Api(app)

api = swagger.docs(Api(app), apiVersion='0.1',
                   basePath='http://localhost:5000',
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/pbs/api/spec',
                   description='The Cloudmesh PBS REST API')

class Job(restful.Resource):

   def get(self, id):
       """gets all jobs"""
       return {'name': 'job get ' + str(id)}

#
# NOTE RESPONSE MSG IS DUMMY I DID NOT WORK ON THAT YET
#
class JobList(restful.Resource):
    @swagger.operation(
        notes='Listing of PBS jobs on a host',
        responseClass=__name__,
        nickname='joblist',
        parameters=[
            {
              "name": "host",
              "description": "The name of the host on which we list the jobs",
              "required": True,
              "allowMultiple": False,
              "dataType": "String",
              "paramType": "path"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. The URL of the created blueprint should be in the Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, host):
       """gets all jobs"""
       pbs = OpenPBS(deploy=True)       
       manager = pbs.manager(host)
       r = pbs.qstat(host, user=False, format="dict")
       return r

class QueueList(restful.Resource):

    @swagger.operation(
        notes='Listing of the PBS queues on a host',
        responseClass=__name__,
        nickname='joblist',
        parameters=[
            {
              "name": "host",
              "description": "The name of the host on which we list the queues",
              "required": True,
              "allowMultiple": False,
              "dataType": "String",
              "paramType": "path"
            }
          ],
        responseMessages=[
            {
              "code": 201,
              "message": "Created. The URL of the created blueprint should be in the Location header"
            },
            {
              "code": 405,
              "message": "Invalid input"
            }
          ]
        )
    def get(self, host):
       """gets all jobs"""
       return {'name': 'queue get ' + str(id)}

api.add_resource(JobList, '/pbs/job/<host>')   
# api.add_resource(Job, '/pbs/job/<id>')
api.add_resource(QueueList, '/pbs/queue/<host>')

if __name__ == '__main__':
    print "test with"
    print "Window 1-> python cloudmesh_pbs/service.py"
    print "Window 2-> curl http://127.0.0.1:5000/pbs/india/job"
    print 
    print "Swagger -> http://127.0.0.1:5000/pbs/api/spec"
    print "  http://127.0.0.1:5000/pbs/api/spec"
    app.run(debug=True)

