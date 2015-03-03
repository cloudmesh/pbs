import shelve


class pbs_db(object):
    
    def __getitem__(self, id):
        return self.data[id]
        
    def __setitem__(self, id, value):
        self.data[id] = value
        
    def get(self, id):
        pass
    
    def set(self, id, value):
        pass
    
    def clear(self):
        pass
    
    def save(self):
        pass
    
    def load(self):
        pass
    
    
    
class pbs_shelve(pbs_db):    
    
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
    
    def clear(self):
        os.remove(self.filename)
    
    def keys(self):
        self.data.keys()
        
    def delete(self, id):
        del self.data[id]

    def close(self):
        self.data.close()
