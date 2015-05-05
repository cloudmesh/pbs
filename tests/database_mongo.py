from cloudmesh_base.util import HEADING
from cloudmesh_base.util import path_expand


from cloudmesh_pbs.database import DatabaseMongo
import os

# TODO implement test cases

class TestDatabaseMongo:

    def setup(self):
        # HEADING()
        self.db = DatabaseMongo()
        
    def teardown(self):
        # HEADING()
        pass

    def test_clean(self):
        HEADING()
        self.db.clean()
        dbpath = self.db.config['dbpath']
        logpath = self.db.config['dbpath']
            
        assert not os.path.isfile(path_expand(dbpath)) and os.path.isfile(path_expand(logpath)) 

    def test_init(self):
        HEADING()
        print ("TODO")
        assert False
        
    def test_set(self):
        HEADING()
        print ("TODO")
        assert False
        
    def test_update(self):
        HEADING()
        print ("TODO")
        assert False
