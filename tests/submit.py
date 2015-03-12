from cloudmesh_base.util import HEADING
from cloudmesh_base.util import banner

from cloudmesh_pbs.database import pbs_db
from cloudmesh_pbs.pbs import PBS
from cloudmesh_base.xshellutil import xmkdir

from pprint import pprint

import os
 
class TestPBSubmit:
 
    filename = "pbs.db"
    host = "india"
    script = """
    uname -a
    """

    def setup(self):
        # HEADING()

        self.pbs = PBS(deploy=True)
        self.manager = self.pbs.manager(self.host)

        #self.db = pbs_db(self.filename)
        
    def teardown(self):
        # HEADING()
        pass

    # def test_clear(self):
    #     HEADING()
    #     self.db.clear()
    #     assert not os.path.isfile(self.filename)

    def test_generate_script(self):

        banner("Create Dir")
        xmkdir(self.manager, "~/scripts/test")

        # print(self.pbs)

        assert self.pbs.data.get("cloudmesh.pbs.{0}.manager".format(self.host))

        script_template = self.pbs.read_script("etc/job.pbs")
        jobname = "job-" + self.pbs.jobid_get()
        job_script = self.pbs.create_script(jobname, self.script, script_template)
        print(job_script)

        assert "uname" in job_script


    def test_job_submit(self):
        xmkdir(self.manager, "~/scripts/test")

        self.pbs.jobid_incr()

        banner('qsub')

        jobname = "job-" + self.pbs.jobid_get() + ".pbs"

        print(jobname)
        print (self.host)
        script_template = self.pbs.read_script("etc/job.pbs")
        r = self.pbs.qsub(jobname, self.host, 'echo "Hello"', template=script_template)
        pprint(r)
        #banner('variable list')
        #pprint(self.pbs.variable_list(r))
        assert len(r.keys()) == 1


        banner('status')
        jobid = self.pbs.getid(r)
        print (jobid)
        r = self.pbs.jobstatus(self.host, jobid)
        print(r)

        #r = self.pbs.qstat("india")

        #banner("RESULT")

        #pprint(r)

    """
    @classmethod
    def setup_class(cls):
        print ("setup_class() before any methods in this class")

    @classmethod
    def teardown_class(cls):
        print ("teardown_class() after any methods in this class")

    def test_clear(self):
        HEADING()
        self.db.clear()
        assert not os.path.isfile(self.filename)


    def test_set(self):
        HEADING()
        self.db["element"] = "test"
        assert self.db['element'] == "test"
        a = a


    print(pbs.jobid_get())
    pbs.jobid_set(100)
    print(pbs.jobid_get())
    pbs.jobid_incr()




    banner('status')
    jobid = pbs.getid(r)
    r = pbs.jobstatus(host, jobid)

    pprint (r)

    r = pbs.qstat("india")

    banner("RESULT")

    pprint(r)

    '''
    #os.system ("cat " + jobname)
    print()

    db = pbs_shelve("pbd.shelve")

    id = pbs.getid(r)

    db[id] = r

    pprint (db[id])
    '''

    '''
    print("Hosts:", pbs.servers())
    print ("Queues", pbs.queues("delta"))
    print ("Queues", pbs.queues("karst"))

    print(pbs.qstat(host))
    print(pbs.qstat(host, user="*"))
    print(pbs.qstat(host, user="*", format="xml"))
    print(json.dumps(pbs.qstat(host, user="*", format="dict"), indent=4))
    print(pbs.username("bigred"))
    '''
"""