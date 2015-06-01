"""
run with
python setup.py install; nosetests --nocapture tests/test_jobdb.py
python setup.py install; nosetests tests/test_jobdb.py
"""

from cm_mongodb import JobDB
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

    def test_002_stop(self):
        """
        tests if the mongo db can be shutdown
        :return:
        """
        self.db.stop()
        result = True
        assert result

    def test_003_connect(self):
        """
        tests if a mongo db can be connected to
        :return:
        """
        self.db.connect()

        result = True
        assert result

    def test_004_clear(self):
        """
        tests clearing all jobs from the db
        :return:
        """
        self.db.clear()

        # assert not os.path.isfile(path_expand("~/.cloudmesh/pbs/pbs.db"))
        assert(len(self.db) == 0)

    def test_005_init(self):
        #HEADING()
        print (self.db)

    def test_006_add(self):
        """
        tests adding jobs to the db
        :return:
        """
        db = self.db

        count = 5

        db.connect()

        db.deleteJobs()

        for id in range(0,count):
            job = db.insert("job" + str(id))

        assert len(db) == count

    def test_007_delete(self):
        """
        tests deleting a single job from the db
        :return:
        """
        db = self.db

        db.connect()
        job = db.insertJob("deleteme")
        before_count = len(db)

        job = db.deleteJobs("job_name", "deleteme")
        after_count = len(db)

        assert(before_count - after_count == 1)


    def test_008_modify(self):
        """
        tests modifying a single job in the db
        :return:
        """
        db = self.db

        db.connect()

        job = {"job_name": "modifyme", "input_filename":"file1"}

        db.add(job)

        originalFilename = self.db.findJobs("job_name", "modifyme")[0]["input_filename"]

        job = {"job_name": "modifyme", "input_filename":"file2"}

        db.modify(job)

        newFilename = self.db.findJobs("job_name", "modifyme")[0]["input_filename"]

        assert(originalFilename != newFilename)
