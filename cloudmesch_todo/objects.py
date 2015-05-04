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

class Jobmanager(object):

    def add(self, script, inputs, outputs):
        """adds a general job, returns the id"""

    def kill(self, id):
        """removes the job with the given id"""

    def wait(self, timeoout=None, state="C-completed"):
        """Waits for the job to reach the state"""

    def submit (id, host):
        """submits the job with the given id on the host"""

    def get_inputs(self, id):
        """copies the input of the job withthe id to the host
        it is submitted on."""

    def info(self,id):
        """prints the info of the job. including the job state and the
        state of io transfers."""

    def progress(self,id):
        """prints the progers of the job"""


    def find(self, id):
        """same as info"""

    def query(self, query):
        """

            seach must be possible based on

                scriptname
                inputs
                outputs
                status of job
                status of file transfers for job

        """

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


# API

#
class FileRepository(object):

    def find_file(self host, filename):
        """returns a list of tuples (host, location)
        that specifies the location of the file on that host"""


    def set_basedir(self,host, path):
        """sets the basepath of the host under which all
        files can be found"""

    def copy (self, source_host, dest_host, filename):
        """copies the file asynchronously
        from the source to the destination.
        Returns an id to refer to this task"""

    def status(self, id):
        """returns the status of the copy task"""

    def kill(self,id):
        """removes thecopy task with the given id"""

    def delete(self, host, file):
        """removes the file from the host"""

    def wait(self, id, timeout=None):
        """
        :param id: if timeout is none waits indevenetly for the
        task to be completed or failed. If the timeout is
        specifies returns after the timeout is reached"""
        :id: the task id
        :param timeout: the timeout value

    def find_by_status(self, host, state):
        """returns all tasks in the given state"""

    def progress(self,id):
        """returns the progress of the transfer"""

    def usage (self, host):
        """prints usage information of the current storage used"""

    def performance (self, id):
        """returns the overall transfer rate"""

    def units(self, size="G", transfer='GB/s'):
        """sets the units of the transfer and filesize"""

# YAML
# india-filerepo:
#    base: /home/gregor/project/experiment_1
#    user: gregor  # will be used fron ssh conf
#    limit: 10G # maximum size in the repo
#    transferlimit: 1G # maximum size of a file that can be transferred
#    service: # type of the service (ssh, ...)
