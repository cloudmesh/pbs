from cloudmesh_job.cm_jobdb import JobDB


class CommandJob(object):
    @classmethod
    def start(cls):
        db = JobDB()
        db.start()
        Console.ok("job server start")

    @classmethod
    def stop(cls):
        db = JobDB()
        db.stop()
        Console.ok("job server stop")

