"""
run with
python setup.py install; nosetests -v --nocapture tests/test_job_command.py
python setup.py install; nosetests tests/test_job_command.py
"""

import subprocess
from cloudmesh_job.cm_jobdb import JobDB
from cloudmesh_base.util import HEADING
import os

def _execute(cmd):
    print "Testing:", cmd
    command = cmd.split(" ")
    # print command

    result = subprocess.check_output(command)
    return result

# nosetest --nocapture
class TestJobDB:

    def setup(self):
        # HEADING()
        pass

    def teardown(self):
        # HEADING()
        pass

    def test_001_stat(self):
        """
        tests if the mongo db can be started
        :return:
        """
        HEADING()
        result = _execute("cm job stat")
        print result
        assert "0" in result

    def test_002_list(self):
        """
        tests if the mongo db can be started
        :return:
        """
        HEADING()
        result = _execute("cm job list")
        print result
        assert True

    def test_002_add(self):
        """
        tests if the mongo db can be started
        :return:
        """
        HEADING()
        result = _execute("cm job add job1")
        print result
        assert True

    '''
    def test_001_start(self):
        """
        tests if the mongo db can be started
        :return:
        """
        HEADING()
        result = _execute("cm job server start")
        print result
        assert True
    '''

    '''
    def test_003_connect(self):
        """
        tests if a mongo db can be connected to
        :return:
        """
        HEADING()
        self.db.connect()

        result = True
        assert result

    def test_004_clear(self):
        """
        tests clearing all jobs from the db
        :return:
        """
        HEADING()
        db = self.db
        db.connect()

        db.clear()

        # assert not os.path.isfile(path_expand("~/.cloudmesh/pbs/pbs.db"))
        assert(len(db) == 0)


    def test_006_add(self):
        """
        tests adding jobs to the db
        :return:
        """
        HEADING()
        db = self.db

        count = 5

        db.connect()

        db.delete_jobs()

        for id in range(0,count):
            job = db.insert("job" + str(id))

        assert len(db) == count

    def test_007_delete(self):
        """
        tests deleting a single job from the db
        :return:
        """
        HEADING()
        db = self.db

        db.connect()
        job = db.insert("deleteme")
        before_count = len(db)

        job = db.delete_jobs("job_name", "deleteme")
        after_count = len(db)

        assert(before_count - after_count == 1)

    def test_008_modify(self):
        """
        tests modifying a single job in the db
        :return:
        """
        HEADING()
        db = self.db

        db.connect()

        job = {"job_name": "modifyme", "input_filename":"file1"}

        db.add(job)

        originalFilename = self.db.find_jobs("job_name", "modifyme")[0]["input_filename"]

        job = {"job_name": "modifyme", "input_filename":"file2"}

        db.modify(job)

        newFilename = self.db.find_jobs("job_name", "modifyme")[0]["input_filename"]

        assert(originalFilename != newFilename)


    def test_010_info(self):
        """
        prints the info about the db
        :return:
        """
        HEADING()
        db = self.db

        db.connect()
        db.info()
        pass

    def test_011_len(self):
        """
        tests modifying a single job in the db
        :return:
        """
        HEADING()
        db = self.db

        db.connect()
        count = len(db)
        print count
        assert count == 6


    def test_999_stop(self):
        """
        tests if the mongo db can be shutdown
        :return:
        """
        HEADING()
        self.db.stop()
        result = True
        assert result
    '''