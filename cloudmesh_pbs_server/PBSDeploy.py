from __future__ import print_function
from cloudmesh_base.ConfigDict import ConfigDict
from cloudmesh_base.locations import config_file
from cloudmesh_base.xshellutil import xcopy
from cloudmesh_base.Shell import Shell
from cloudmesh_pbs_server.PBSDeploy import PBS

class PBSDeploy(object):

    def load(self):
        self.filename = config_file("/cloudmesh_pbs.yaml")
        self.data = ConfigDict(filename=self.filename)

    def __init__(self, deploy=False):
        if deploy:
            self.deploy()
        self.load()

    def __str__(self):
        return self.data.json()

    @staticmethod
    def deploy(force=True):
        """copies the yaml file from etc in the distribution to the .cloudmesh
        directory. If the file exits it will not be copied and a warning is
        thrown. If the file is the same as in etc no warning is thrown.
        """
        xcopy("../etc/", "~/.cloudmesh", "*.yaml", force=force)

    def servers(self):
        return self.data["cloudmesh"]["pbs"].keys()

    def queues(self, server):
        server = self.data["cloudmesh"]["pbs"][server]
        if "queues" in server:
            return server["queues"]
        else:
            return None

    @staticmethod
    def qstat(host):
        return Shell.ssh(host, "qstat").rstrip()

if __name__ == "__main__":

    config = PBS(deploy=True)

    print(config)

    print("Hosts:", config.servers())

    print ("Queues", config.queues("delta"))
    print ("Queues", config.queues("karst"))

    print(config.qstat("india"))
