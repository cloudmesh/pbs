from cloudmesh_base.util import HEADING
from cloudmesh_base.util import path_expand

from DbPBS.DbPBS import pbs_db
import os
 
class TestDatabase:

    def setup(self):
        # HEADING()
        self.db = pbs_db()
        
    def teardown(self):
        # HEADING()
        pass

    def test_clear(self):
        HEADING()
        self.db.clear()
        assert not os.path.isfile(path_expand("~/.cloudmesh/pbs/pbs.db"))

    def test_init(self):
        HEADING()
        print (self.db)

    def test_set(self):
        HEADING()
        self.db["element"] = "test"
        assert self.db['element'] == "test"

    def test_update(self):
        HEADING()
        self.db.update(host="india")
        self.db.list()
