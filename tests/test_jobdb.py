"""
run with
python setup.py install; nosetests --nocapture -v tests/test_jobdb.py
python setup.py install; nosetests tests/test_jobdb.py
python setup.py install; nosetests -v --nocapture tests/test_jobdb.py:TestJobDB.test_001_start

"""
from __future__ import print_function

from cloudmesh_job.cm_jobdb import JobDB
from cloudmesh_base.util import HEADING
from cloudmesh_base.Shell import Shell
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
        HEADING()
        self.db.start()
        up = self.db.isup()
        result = up
        assert result
        
    def test_002_up(self):
        """
        tests if the mongo db can be started
        :return:
        """
        HEADING()
        up = self.db.isup()
        print (up)
        self.db.stop()
        down = not self.db.isup()
        self.db.start()
        assert up and down

    def test_003_pid(self):
        """
        tests if the mongo db can be started
        :return:
        """
        HEADING()
        pid = self.db.pid()
        print (pid)
        assert True

    def test_004_connect(self):
        """
        tests if a mongo db can be connected to
        :return:
        """
        HEADING()
        self.db.connect()

        result = True
        assert result

    def test_005_clear(self):
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
        print ("AAA")
        before_count = len(db)
        print ("CCC", len(db))
        job = db.insert("deleteme")
        print ("DDD", len(db))

        job = db.delete_jobs("job_name", "deleteme")
        print ("EEE")
        after_count = len(db)
        print ("FFF", len(db))
        assert(before_count - after_count == 0)

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
        print (count)
        assert count == 6

    def test_012_yaml_load(self):
        """
        tests adding jobs from a YAML file
        :return:
        """
        HEADING()
        db = self.db
        db.connect()

        # Clear all jobs currently in the database to ensure a correct final assertion
        db.clear()

        # Add the jobs outlined in the YAML file
        db.add_from_yaml("etc/jobs.yaml")

        count_fgrep = len(Shell.fgrep("input:", "etc/jobs.yaml").split("\n"))

        # Assert that the correct number jobs have been added
        assert(db.count() == count_fgrep)

    def test_013_find_files(self):
        """
        tests searching for a file
            the file being searched for exists in 3 files: twice as input and twice as output
        :return:
        """
        HEADING()
        db = self.db

        db.connect()

        # Clear all jobs currently in the database to ensure a correct final assertion
        db.clear()

        # Add the jobs outlined in the YAML file
        db.add_from_yaml("etc/jobs.yaml")
        inputs, outputs = db.find_jobs_with_file("in1.txt")

        # Assert that the lengths of the inputs and outputs arrays are correct
        count_fgrep = len(Shell.fgrep("in1.txt", "etc/jobs.yaml").strip().split("\n"))
        assert(len(inputs) == count_fgrep)


    def test_14_jobid(self):
        HEADING()
        db = self.db

        db.connect()

        db.set_jobid(11)

        a = db.get_jobid()
        db.incr_jobid()
        b = db.get_jobid()

        print (a, b)
        assert b == a + 1

    def test_15_jobscript(self):
        HEADING()
        db = self.db
        db.connect()

        name = "test1"
        contents = "hallo"

        db.add_script(name, contents)
        db.add_script("test2", "other")
        script = db.get_script(name)

        print ("Script:", script)
        print ("Content:", contents)

        db.write_script(name, "/tmp/script.txt")
        what = Shell.cat("/tmp/script.txt")

        assert contents == what
        assert contents == script



    def test_999_stop(self):
        """
        tests if the mongo db can be shutdown
        :return:
        """
        HEADING()
        self.db.stop()
        result = True
        assert result
