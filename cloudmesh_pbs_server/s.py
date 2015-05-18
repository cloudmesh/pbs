'''
Running:

  PYTHONPATH=. python examples/basic.py

'''

from flask import Flask, redirect
from flask.ext.restful import reqparse, abort, Api, Resource, fields,\
    marshal_with
from flask_restful_swagger import swagger

app = Flask(__name__, static_folder='../static')

###################################
# This is important:
api = swagger.docs(Api(app), apiVersion='0.1',
                   basePath='http://localhost:5000',
                   resourcePath='/',
                   produces=["application/json", "text/html"],
                   api_spec_url='/pbs/api/spec',
                   description='The Cloudmesh PBS REST API')
###################################

JOBS = {
    'job1': {'task': 'build an API'},
    'job2': {'task': '?????'},
    'job3': {'task': 'profit!'},
}


def abort_if_job_doesnt_exist(job_id):
  if job_id not in JOBS:
    abort(404, message="Job {} doesn't exist".format(job_id))

parser = reqparse.RequestParser()
parser.add_argument('task', type=str)


@swagger.model
class JobItem:
  """This is an example of a model class that has parameters in its constructor
  and the fields in the swagger spec are derived from the parameters
  to __init__.
  In this case we would have args, arg2 as required parameters and arg3 as
  optional parameter."""
  def __init__(self, arg1, arg2, arg3='123'):
    pass

class Job(Resource):
  "Cloudmesh Job API"
  @swagger.operation(
      notes='get a job item by ID',
      nickname='get',
      # Parameters can be automatically extracted from URLs (e.g. <string:id>)
      # but you could also override them here, or add other parameters.
      parameters=[
          {
            "name": "job_id_x",
            "description": "The ID of the JOB item",
            "required": True,
            "allowMultiple": False,
            "dataType": 'string',
            "paramType": "path"
          },
          {
            "name": "a_bool",
            "description": "The ID of the JOB item",
            "required": True,
            "allowMultiple": False,
            "dataType": 'boolean',
            "paramType": "path"
          }
      ])
  def get(self, host, job_id, ):
    # This goes into the summary
    """Get a pbs job

    Returns the job based on finding it by jobid on the specified host
    """
    abort_if_job_doesnt_exist(job_id)
    return JOBS[job_id], 200, {'Access-Control-Allow-Origin': '*'}

  @swagger.operation(
      notes='delete a pbs job by ID',
  )
  def delete(self, host, job_id):
    abort_if_job_doesnt_exist(job_id)
    del JOBS[job_id]
    return '', 204, {'Access-Control-Allow-Origin': '*'}

  @swagger.operation(
      notes='edit a pbs job by ID',
  )
  def put(self, host, job_id):
    args = parser.parse_args()
    task = {'task': args['task']}
    JOBS[job_id] = task
    return task, 201, {'Access-Control-Allow-Origin': '*'}

  def options (self, **args):
    # since this method is not decorated with @swagger.operation it does not
    # get added to the swagger docs
    return {'Allow' : 'GET,PUT,POST,DELETE' }, 200, \
    { 'Access-Control-Allow-Origin': '*', \
      'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE', \
      'Access-Control-Allow-Headers': 'Content-Type' }

# JobList
#   shows a list of all jobs, and lets you POST to add new tasks
class JobList(Resource):

  def get(self):
    return JOBS, 200, {'Access-Control-Allow-Origin': '*'}

  @swagger.operation(
      notes='Creates a new JOB item',
      responseClass=JobItem.__name__,
      nickname='create',
      parameters=[
          {
            "name": "body",
            "description": "A JOB item",
            "required": True,
            "allowMultiple": False,
            "dataType": JobItem.__name__,
            "paramType": "body"
          }
      ],
      responseMessages=[
          {
              "code": 201,
              "message": "Created. The URL of the created blueprint should " +
              "be in the Location header"
          },
          {
              "code": 405,
              "message": "Invalid input"
          }
      ])
  def post(self):
    args = parser.parse_args()
    job_id = 'job%d' % (len(JOBS) + 1)
    JOBS[job_id] = {'task': args['task']}
    return JOBS[job_id], 201, {'Access-Control-Allow-Origin': '*'}

@swagger.model
class ModelWithResourceFields:
  resource_fields = {
      'a_string': fields.String()
  }

@swagger.model
@swagger.nested(
   a_nested_attribute=ModelWithResourceFields.__name__,
   a_list_of_nested_types=ModelWithResourceFields.__name__)
class JobItemWithResourceFields:
  """This is an example of how Output Fields work
  (http://flask-restful.readthedocs.org/en/latest/fields.html).
  Output Fields lets you add resource_fields to your model in which you specify
  the output of the model when it gets sent as an HTTP response.
  flask-restful-swagger takes advantage of this to specify the fields in
  the model"""
  resource_fields = {
      'a_string': fields.String(attribute='a_string_field_name'),
      'a_formatted_string': fields.FormattedString,
      'an_enum': fields.String,
      'an_int': fields.Integer,
      'a_bool': fields.Boolean,
      'a_url': fields.Url,
      'a_float': fields.Float,
      'an_float_with_arbitrary_precision': fields.Arbitrary,
      'a_fixed_point_decimal': fields.Fixed,
      'a_datetime': fields.DateTime,
      'a_list_of_strings': fields.List(fields.String),
      'a_nested_attribute': fields.Nested(ModelWithResourceFields.resource_fields),
      'a_list_of_nested_types': fields.List(fields.Nested(ModelWithResourceFields.resource_fields)),
  }

  # Specify which of the resource fields are required
  required = ['a_string']

  swagger_metadata = {
      'an_enum': {
          'enum': ['one', 'two', 'three']
      }
  }

class MarshalWithExample(Resource):
  @swagger.operation(
      notes='get something',
      responseClass=JobItemWithResourceFields,
      nickname='get')
  @marshal_with(JobItemWithResourceFields.resource_fields)
  def get(self, **kwargs):
    return {}, 200,  {'Access-Control-Allow-Origin': '*'}


##
## Actually setup the Api resource routing here
##
api.add_resource(JobList, '/pbs')
api.add_resource(Job, '/pbs/<string:host>/<string:job_id>')
api.add_resource(MarshalWithExample, '/marshal_with')


@app.route('/docs')
def docs():
  return redirect('/static/docs.html')


if __name__ == '__main__':
  JobItemWithResourceFields()
  JobItem(1, 2, '3')
  app.run(debug=True)
