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


def find_file(filename):
    """returns the file location in a repository"""

