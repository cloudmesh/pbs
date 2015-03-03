from __future__ import print_function
from cloudmesh.config.ConfigDict import ConfigDict
from cloudmesh_install import config_file
from api.xshellutil import xcopy
from cloudmesh.shell.Shell import Shell


class PBS(object):

    def load(self):
        self.filename = config_file("/cloudmesh_pbs.yaml")
        self.data = ConfigDict(filename=self.filename)

    def __init__(self, deploy=False):
        if deploy:
            self.deploy()
        self.load()

    def __str__(self):
        return self.data.json()

    def deploy(self, force=True):
        """copies the yal file from etc in the distribution to the .cloudmesh
        directory. If the file exits it will not be copied and a warning is
        thrown. If the file is the same as in etc no warning is thrown.
        """
        xcopy("../etc/", "~/.cloudmesh", "*.yaml", force=force)

    def servers(self):
        return config.data["cloudmesh"]["pbs"].keys()

    def queues(self, server):
        server = config.data["cloudmesh"]["pbs"][server]
        if "queues" in server:
            return server["queues"]
        else:
            return None

    def qstat(self, host):

        return Shell.ssh(host, "qstat").rstrip()

if __name__ == "__main__":


    config = pbs_config(deploy=True)

    print(config)

    print("Hosts:", config.servers())

    print ("Queues", config.queues("delta"))
    print ("Queues", config.queues("karst"))

    print(config.qstat("india"))
