from __future__ import print_function

import os
import abc
import shelve
from pprint import pprint

from cloudmesh_base.tables import dict_printer
from cloudmesh_base.Shell import Shell
from cloudmesh_base.util import banner
from cloudmesh_base.util import path_expand

from cloudmesh_pbs.OpenPBS import OpenPBS


class pbs_db_interface(object):
    __metaclass__ = abc.ABCMeta

    db = None

    def data(self):
        return dict(self.db)

    def __getitem__(self, index):
        return self.db[index]

    def __setitem__(self, index, value):
        self.db[index] = value

    @abc.abstractmethod
    def load(self, filename):
        """loads the saved databsa from the file"""

    @abc.abstractmethod
    def get(self, id):
        """get the object with the id"""

    @abc.abstractmethod
    def set(self, id, value):
        """set the objet with the id to value"""

    def set_filename(self, filename):
        """set the objet with the id to value"""
        self.filename = filename

    def remove(self):
        try:
            os.remove(self.filename)
        except:
            pass

    @abc.abstractmethod
    def save(self):
        """save the cloudmesh_job"""

    @abc.abstractmethod
    def update(self):
        """load the cloudmesh_job"""


class DbPBS(pbs_db_interface):
    def __init__(self, filename=None):
        self.pbs = OpenPBS(deploy=True)
        self.open()

    def open(self, filename=None):
        if filename is not None:
            self.filename = filename
        else:
            self.filename = path_expand(self.pbs.database_filename())
        path = os.path.dirname(self.filename)
        Shell.mkdir(path)
        self.load()

    def clear(self):
        for id in self.db:
            del self.db[id]
        self.save()

    def load(self):
        """load the cloudmesh_job"""
        print('loading', self.filename)
        # remove db ending so that shelve automatically adds it
        self.filename = self.filename.replace(".db", "")
        self.db = shelve.open(self.filename, writeback=True)

    def save(self):
        self.db.sync()

    def get(self, id):
        return self.db[id]

    def status(self, id):
        return self.get(id)["job_state"]

    def set(self, id, value):
        self.db[id] = value
        self.save()

    def keys(self):
        self.data().keys()

    def delete(self, id):
        del self.db[id]

    def close(self):
        self.db.close()

    def update(self, host=None, user=True):
        if host is None:
            print("host is none is not supported yet")
            raise
        print("QSTAT")
        r = dict(self.pbs.qstat(host, user=user, format='dict'))
        pprint(r)
        if r is not {}:
            for jobid in r:
                self.db[jobid] = r[jobid]
            self.save()
        else:
            print("no jobs found after query")
        print("update completed")

    def info(self):
        print("Filename:", self.filename)

    def list(self, attributes=None, output="table"):
        if self.db is None or len(self.db) == 0:
            print("No jobs found")
            return None
        columns = attributes
        if columns is None:
            columns = ["cm_jobid", "cm_host", "cm_user", "Job_Name", "job_state", "exit_status"]

        # prepare the dict
        d = {}
        for jobid in self.db:
            content = {}
            for attribute in columns:
                try:
                    content[attribute] = self.db[jobid][attribute]
                except:
                    content[attribute] = "None"
            d[jobid] = content

        # print the dict
        if output in ["csv", "table", "dict", "yaml"]:
            return dict_printer(d, order=columns, output=output)
        return None

    def qsub(self, name, host, script, template=None, kind="dict"):
        r = self.pbs.qsub(name, host, script, template=template, kind=kind)
        pprint(r)
        return dict(r)


if __name__ == "__main__":

    qsub = False

    db = DbPBS()
    db.clear()
    db.info()
    db.update(host="india", user=False)
    print(db.list(output="table"))
    print(db.list(output="csv"))
    print(db.list(output="dict"))
    print(db.list(output="yaml"))

    banner("user")
    db.clear()
    db.update(host="india")
    print(db.list(output="table"))

    if qsub:
        banner('qsub')

        pbs = OpenPBS()
        jobname = "job-" + pbs.jobid + ".pbs"
        host = "india"

        script_template = pbs.read_script("etc/job.pbs")
        print(script_template)

        r = db.qsub(jobname, host, 'echo "Hello"', template=script_template)
        pprint(r)
        banner('variable list')
        pprint(OpenPBS.variable_list(r))