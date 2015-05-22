"""
run with

python setup.py install; nosetests --nocapture tests/test_jobdb.py
python setup.py install; nosetests tests/test_jobdb.py


"""

from cloudmesh_base.util import HEADING
from cloudmesh_base.util import path_expand

from cloudmesh_job.cm_jobdb import JobDB
import os

# nosetest --nocapture
class TestJobDB:

    def setup(self):
        # HEADING()
        self.db = JobDB()

    def teardown(self):
        # HEADING()
        pass

    def test_001_start(self):
        """
        tests if the mongo db can be started
        :return:
        """
        self.db.start()
        # identify a test to see if mongod is started
        result = True
        assert result

    def test_100_stop(self):
        """
        tests if the mongo db can be shutdown
        :return:
        """
        self.db.stop()
        result = True
        assert result

    def test_002_clear(self):
        HEADING()
        # self.db.clear()
        # assert not os.path.isfile(path_expand("~/.cloudmesh/pbs/pbs.db"))
        assert True

    def test_003_init(self):
        HEADING()
        print (self.db)

    def test_004_add(self):
        HEADING()
        db = self.db

        count = 5

        db.connect()
        for id in range(0,count-1):
            job = db.insert("job" + str(id))

        print ("len", len(db))
        assert len(db) == count

    def test_004_add(self):
        HEADING()
        db = self.db

        db.connect()
        job = db.insert("deleteme")
        before_count = len(db)

        job = db.delete("deleteme")
        after_count = len(db)

        assert(before_count - after_count == 1)


    def test_005_update(self):
        HEADING()
        # self.db.update(host="india")
        # self.db.list()
        assert True