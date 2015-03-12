import abc
import os
from pprint import pprint
import shelve

from cloudmesh_pbs.pbs import PBS
from cloudmesh_base.util import banner


class pbs_db_interface(object):
    __metaclass__  = abc.ABCMeta
    
    def __getitem__(self, id):
        return self.data[id]
        
    def __setitem__(self, id, value):
        self.data[id] = value

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
        
    def clear(self):
        try:
            os.remove(self.filename)
        except:
            pass
        
    @abc.abstractmethod        
    def save(self):
        """save the database"""
 
    @abc.abstractmethod        
    def update(self):
        """load the database"""
      
class pbs_db(pbs_db_interface):    
    
    def __init__(self, filename):
        self.filename = filename
        self.load()
        self.pbs = PBS(deploy=True)    
    
    def load(self):
        """load the database"""
        self.data = shelve.open(self.filename, writeback = True) 
   
    def save(self):
        self.data.sync()
        
    def get(self, id):
        return self.data[id]
    
    def set(self, id, value):
        self.data[id] = value
        self.save()
        
    def keys(self):
        self.data.keys()
        
    def delete(self, id):
        del self.data[id]

    def close(self):
        self.data.close()
        
    def update(self, user=True, host=None):        
        self.load()
        r = self.pbs.qstat(host, user=user, format='dict')
        for jobid in r:
            self.data[jobid] = r[jobid]
            
        self.save()

    def list(self, attributes):
        for jobid in self.data:
            content = []
            for attribute in attributes:
                try:
                    content.append(self.data[jobid][attribute])
                except:
                    content.append("None")
                    
            print (",".join(content))
        
if __name__ == "__main__":
    
    host = "india"
    pbs = PBS(deploy=True)
    jobname = "job-" + pbs.jobid_get() + ".pbs"
    script_template = pbs.read_script("etc/job.pbs")
    r = pbs.qsub(jobname, host, 'echo "Hello"', template=script_template)
    pprint(r)
    
    filename = "qstat-shelve"
    
    db = pbs_db(filename)
    db.clear()
    
    
    db = pbs_db(filename)
    
    # key = "gregor"
    # element = {"name": "gregor", "home": "."}
    # db[key] = element
    # print (db[key])
    
    db.update(host="india")
    attributes = ["cm_jobid", "cm_host",  "cm_user", "Job_Name",  "job_state", "exit_status"]
    banner("LIST")
    db.list(attributes)
