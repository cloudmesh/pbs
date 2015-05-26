from flask import Flask
import cm_generate_command
app = Flask(__name__)

@app.route('/start')
def start():
	return 'Starting Mongo'

@app.route('/stop')
def stop():
	return 'Stopping Mongo'

@app.route('/info')
def info():
	return 'Showing info'

@app.route('/connect')
def connect():
	return 'Connecting to DB'

@app.route('/modify')
def modify():
	return 'Modifying'

@app.route('/add')
def add():
	return 'adding'

@app.route('/insert')
def insertJob():
	return 'Inserting Job'

@app.route('/find')
def findJobs():
	return 'finding jobs'

@app.route('/delete')
def delete():
	return 'Deleting jobs'

@app.route('/Count')
def startMongo():
	return 'counting jobs'

@app.route('/update_job_end_time')
def update_job_end_time():
	return 'Starting update_job_end_time'

@app.route('/updateJobAttributes')
def updateJobAttributes():
	return 'Starting updateJobAttributes'

@app.route('/jobStatusStats')
def jobStatusStats():
	return 'Starting jobStatusStats'

if __name__ == '__main__':
    app.run()