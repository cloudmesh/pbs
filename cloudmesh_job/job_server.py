from flask import Flask, request
from flask_restful import Resource, Api, reqparse
from cloudmesh_job.cm_jobdb import JobDB

app = Flask(__name__)
api = Api(app)

db = JobDB()


class Insert(Resource):
    '''will insert job by job_id'''

    def put(self, args_job_name):
        db.insert(args_job_name)
        print "will now search for job, if properly inserted, will print out value"
        return db.find_jobs({"job_name": args_job_name})


class Delete(Resource):
    def delete(self, args_job_name):
        '''if job exists, delete'''
        if db.find_jobs(args_job_name):
            db.delete(args_job_name)
            return Console.ok("job has been deleted")
        else:
            return Console.ok("Job not found")


api.add_resource(Insert, '/insert/<string:job_name>')
api.add_resource(Delete, '/delete/<string:job_name>')

'''debug should not be in production code'''
if __name__ == '__main__':
    app.run(debug=True) 
