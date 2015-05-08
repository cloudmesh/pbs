from mongoengine import *
from cloudmesh_base.Shell import Shell


class Database(object):
    """
    This class instantiates a database for storing python objects into it.
    """

    config = {
        'port': 27017,
        'dbpath': "~/.cloudmesh/pbs/data_mongo.db",
        'logpath': "~/.cloudmesh/pbs/data_mongo.log",
        'id': None
    }

    def __init__(self,
                 port=None,
                 dbpath=None,
                 logpath=None):
        """
        Creates a new database with the given datbase and log file path on the port
        :param port: The port to use
        :param dbpath: The database path
        :param logpath: The logpath
        """
        if port is not None:
            self.port = port
        if dbpath is not None:
            self.dbpath = dbpath
        if logpath is not None:
            self.logpath = logpath

    def start(self):
        """
        Starts the database process in the background.
        """
        r = Shell.sh("mongod", "--fork",
                     "--logpath", self.config['logpath'],
                     "--prot", self.config['port'],
                     '--dbpath', self.config['dbpath']
        print(r)
        # TODO
        # get the id from r
        self.config['id'] = None  # put here the real id

    def stop(self):
        """
        Stops the database process
        """
        id = self.config['id'']
        # TODO use pythonic way to kill
        # p = psutil.Process(pid)
        # p.terminate()  #or p.kill()
        r = Shell.kill('-9', id)
        pass

    def clear(self):
        """
        Empties the database from all entries.
        TODO not yet implemented
        """
        pass

    def deploy(self):
        """
        A simple shell based deployment of the database backend.
        It self detects the OS and installs the needed software.
        We assume tht you have sudo and run this command in a virtualenv.
        Supported platforms: OSX, ubuntu, redhat
        TODO implement
        :return:
        """
        pass

    def status(self):
        """
        returns information about the status of teh database such as
        running, unavailable, ...
        TODO determine which states are useful
        :return:
        """
        pass

    def usage(self):
        """
        Retunrsn usage statistics such as how many objects are in it,
        how big the file space, ....
        TODO implement
        :return:
        """
        pass


class CloudmeshEntry(Document):
    created = DateTimeField()
    updated = DateTimeField()


class Job(CloudmeshEntry):
    script = StringField(required=True)
    input = ListField(StringField())
    output = StringField(max_length=50)
    status = StringField()  # c_status
    q_status = StringField()

    meta = {'allow_inheritance': True}


class Jobmanager(object):
    def add(self, script, inputs, outputs):
        """adds a general job, returns the id"""

    def kill(self, id):
        """removes the job with the given id"""

    def wait(self, timeoout=None, state="C-completed"):
        """Waits for the job to reach the state"""

    def submit(id, host):
        """submits the job with the given id on the host"""

    def get_inputs(self, id):
        """copies the input of the job withthe id to the host
        it is submitted on."""

    def info(self, id):
        """prints the info of the job. including the job state and the
        state of io transfers."""

    def progress(self, id):
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
# host: india
# name: batch
# username: gregor
# max_running_jobs: 3
# max_queued_jobs: 3
# active: True
# ...


# API

#
class FileRepository(object):
    def find_file(self host, filename

    ):
    """returns a list of tuples (host, location)
        that specifies the location of the file on that host"""


def set_basedir(self, host, path):
    """sets the basepath of the host under which all
        files can be found"""


def copy(self, source_host, dest_host, filename):
    """copies the file asynchronously
        from the source to the destination.
        Returns an id to refer to this task"""


def status(self, id):
    """returns the status of the copy task"""


def kill(self, id):
    """removes thecopy task with the given id"""


def delete(self, host, file):
    """removes the file from the host"""


def wait(self, id, timeout=None):
    """
        :param id: if timeout is none waits indevenetly for the
        task to be completed or failed. If the timeout is
        specifies returns after the timeout is reached
        :id: the task id
        :param timeout: the timeout value
        """


def find_by_status(self, host, state):
    """returns all tasks in the given state"""


def progress(self, id):
    """returns the progress of the transfer"""


def usage(self, host):
    """prints usage information of the current storage used"""


def performance(self, id):
    """returns the overall transfer rate"""


def units(self, size="G", transfer='GB/s'):
    """sets the units of the transfer and filesize"""  # YAML

# india-filerepo:
# base: /home/gregor/project/experiment_1
#    user: gregor  # will be used fron ssh conf
#    limit: 10G # maximum size in the repo
#    transferlimit: 1G # maximum size of a file that can be transferred
#    service: # type of the service (ssh, ...)
