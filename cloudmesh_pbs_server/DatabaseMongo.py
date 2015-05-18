from __future__ import print_function

from mongoengine import *
from cloudmesh_base.Shell import Shell
from cloudmesh_base.util import path_expand


class DatabaseMongo(object):
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

        for key in ['dbpath', 'logpath']:
            self.config[key] = path_expand(self.config[key])

    def start(self):
        """
        Starts the database process in the background.
        """
        for key in ['dbpath', 'logpath']:
            path = os.dirname(self.config[key])
            Shell.mkdir(path)

        r = Shell.sh("mongod", "--fork",
                     "--logpath", self.config['logpath'],
                     "--prot", self.config['port'],
                     '--dbpath', self.config['dbpath'])
        print (r)
        # TODO
        # get the id from r
        self.config['id'] = None  # put here the real id

    def stop(self):
        """
        Stops the database process
        """
        id = self.config['id']
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

    def statistics(self):
        """
        prints statistics for the database and all of its collections.
        TODO implement
        :return:
        """
        # from pymongo import MongoClient

        # client = MongoClient()
        # db = client.test

        ## print collection statistics
        # print db.command("collstats", "events")

        ## print database statistics
        # print db.command("dbstats")

    def find(self, **kwargs):
        """
        The query issued to the db
        TODO implement
        :param kwargs:
        :return: objects matching the querry
        """

    def save(self):
        """
        saves the database after modifications have been done
        :return:
        TODO implement
        """
        pass

    def add(self, element):
        """
        adds the element to the db (element is specifid as dict
        :param element:
        :return:
        TODO implement
        """
        pass


def test():
    db = DatabaseMongo()

    # if not db.deployed # todo
    db.deploy()
    db.start()

    query = None  # todo this is a dict passes along to mongo implement find function
    db.find(query)
    db.save()
    db.kill()


if __name__ == "__main__":
    test()

