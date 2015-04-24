from flask import Flask
from flask.ext import restful

app = Flask(__name__)
api = restful.Api(app)

# https://flask-restful.readthedocs.org/en/0.3.2/quickstart.html#a-minimal-api

class PbsServer(restful.Resource):
    
    def get(self):
        return {'hello': 'world'}

api.add_resource(PbsServer, '/pbs')

if __name__ == '__main__':
    app.run(debug=True)

    print "test with"
    print "Window 1-> python service.py"
    print "Window 2-> curl http://127.0.0.1:5000/"
