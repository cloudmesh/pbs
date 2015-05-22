my_settings = {
    'MONGO_HOST': 'localhost',
    'MONGO_PORT': 27017,
    'MONGO_DBNAME': 'jobsdb',
    'DOMAIN': {'jobs': {}}
}

from eve import Eve
app = Eve(settings=my_settings)

if __name__ == '__main__':
    app.run()
