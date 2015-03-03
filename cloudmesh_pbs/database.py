import shelve
import abc
import os

class pbs_db_interface(object):
    __metaclass__  = abc.ABCMeta
    
    def __getitem__(self, id):
        return self.data[id]
        
    def __setitem__(self, id, value):
        self.data[id] = value
    
    @abc.abstractmethod        
    def get(self, id):
        """get the object with the id"""
    
    @abc.abstractmethod        
    def set(self, id, value):
        """set the objet with the id to value"""
    
    def clear(self):
        try:
            os.remove(self.filename)
        except:
            pass
        
        
    @abc.abstractmethod        
    def save(self):
        """save the database"""
    
    @abc.abstractmethod        
    def load(self):
        """load the database"""
    
    
class pbs_shelve(pbs_db_interface):    
    
    def __init__(self, filename):
        self.filename = filename
        self.data = shelve.open(self.filename, writeback = True) 

    def load(self):
        self.data = shelve.open(self.filename, writeback = True) 

    def save(self):
        self.data.sync()
        
    def get(self, id):
        return self.data[id]
    
    def set(self, id, value):
        self.data[id] = value
        
    def keys(self):
        self.data.keys()
        
    def delete(self, id):
        del self.data[id]

    def close(self):
        self.data.close()

class pbs_db(pbs_db_interface):
    
    def __init__(self, filename, provider):
        self.filename = filename
        self.data = provider(filename)
    
    def load(self):
        self.data.load()
        
    def save(self):
        self.data.sync()
        
    def get(self, id):
        return self.data[id]
    
    def set(self, id, value):
        self.data[id] = value
    
    def keys(self):
        self.data.keys()
        
    def delete(self, id):
        del self.data[id]

    def close(self):
        self.data.close()
            
if __name__ == "__main__":
    
    db = pbs_shelve("pbd.shelve")
    
    key = "gregor"
    element = {"name": "gregor", "home": "."}
    
    db[key] = element
    
        
    print (db[key])
