class CloudmeshEntry(Document):
    created: DateTimeField()
    updated: DateTimeField()

class Job(CloudmeshEntry):
    script = StringField(required=True)
    input =  ListField(StringField())
    output = StringField(max_length=50)
    status = StringField()   # c_status
    q_status = StringField()

    meta = {'allow_inheritance': True}

class FileRepository(CloudmeshEntry):
    path = StringField()
    endpoint = StringField()
    protocoll = StringField()

    meta = {'allow_inheritance': True}

class File(CloudmeshEntry)
    repo = FileRepository()
    name = StringField()

    meta = {'allow_inheritance': True}

class Queue(CloudmeshEntry)
    name = StringField()
    host = StringField()
    username = StringField()
    max_running_jobs = IntegerField()
    max_queued_jobs = IntegerField()
    active = BooleanField()

# Yaml Example
#
# india-batch:
#     host: india
#     name: batch
#     username: gregor
#     max_running_jobs: 3
#     max_queued_jobs: 3
#     active: True
# ...




def find_file(filename):
    """returns the file location in a repository"""

