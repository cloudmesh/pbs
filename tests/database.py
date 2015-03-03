from cloudmesh_base.base import HEADING
from cloudmesh_pbs.database import pbs_db, pbs_shelve
import os
 
class TestDatabase:
 
    filename = "pbs.db"
    
    def setup(self):
        # HEADING()
        self.db = pbs_db(self.filename, pbs_shelve)
        
    def teardown(self):
        # HEADING()
        pass

    """ 
    @classmethod
    def setup_class(cls):
        print ("setup_class() before any methods in this class")
 
    @classmethod
    def teardown_class(cls):
        print ("teardown_class() after any methods in this class")
     """
    def test_clear(self):
        HEADING()
        self.db.clear()
        assert not os.path.isfile(self.filename) 
        
        
    def test_set(self):
        HEADING()
        self.db["element"] = "test"
        assert self.db['element'] == "test"
