from __future__ import print_function
from cloudmesh.config.ConfigDict import ConfigDict
from cloudmesh_install import config_file
from api.xshellutil import xcopy
from cloudmesh.shell.Shell import Shell
from api.ssh_config import ssh_config
from xml.dom import minidom
import json

class PBS(object):

    def load(self):
        self.filename = config_file("/cloudmesh_pbs.yaml")
        self.data = ConfigDict(filename=self.filename)
        self.hosts = ssh_config()

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
        return self.data["cloudmesh"]["pbs"].keys()

    def queues(self, server):
        server = config.data["cloudmesh"]["pbs"][server]
        if "queues" in server:
            return server["queues"]
        else:
            return None

    def qstat_xml_to_dict(self, xmldata):
        info = {}
        try:
            xmldoc = minidom.parseString(xmldata)

            itemlist = xmldoc.getElementsByTagName('Job')
            for item in itemlist:
                job = {}
                for attribute in item.childNodes:
                    if len(attribute.childNodes) == 1:
                        job[attribute.nodeName] = attribute.firstChild.nodeValue
                    else:
                        job[attribute.nodeName] = {}
                        for subchild in attribute.childNodes:
                            job[attribute.nodeName][
                                subchild.nodeName] = subchild.firstChild.nodeValue
                    if attribute.nodeName in ['Job_Owner']:
                        (name, host) = job[attribute.nodeName].split('@')
                        job[u'cm_user'] = name
                        job[u'cm_host'] = host

                info[job['Job_Id']] = job
        except:
            pass
        try:
            xmldoc = minidom.parseString(xmldata)

            itemlist = xmldoc.getElementsByTagName('Job')
            for item in itemlist:
                job = {}
                for attribute in item.childNodes:
                    if len(attribute.childNodes) == 1:
                        job[attribute.nodeName] = attribute.firstChild.nodeValue
                    else:
                        job[attribute.nodeName] = {}
                        for subchild in attribute.childNodes:
                            job[attribute.nodeName][
                                subchild.nodeName] = subchild.firstChild.nodeValue
                    if attribute.nodeName in ['Job_Owner']:
                        (name, host) = job[attribute.nodeName].split('@')
                        job[u'cm_user'] = name
                        job[u'cm_host'] = host

                info[job['Job_Id']] = job
        except:
            pass
        return info

    def qstat(self, host, user=None, format=None):
        data = None
        if user == "*":
            if format == None:
                data = Shell.ssh(host, "qstat").rstrip()
            elif format in ["xml", "dict"]:
                data = Shell.ssh(host, "qstat", "-x").rstrip()
        elif user == None:
            user = self.username(host)
            if format == None:
                data = Shell.ssh(host, "qstat", "-u", user).rstrip()
            elif format in ["xml", "dict"]:
                data = Shell.ssh(host, "qstat", "-x", "-u", user).rstrip()
            else:
                print ("ERROR: cloudmesh qstat parameters wrong")
        if format in ["dict"]:
            d_data = self.qstat_xml_to_dict(data)
            data = d_data
        return data

    def username(self, host):
        return self.hosts.username(host)

if __name__ == "__main__":

    config = PBS(deploy=True)

    print(config)

    print("Hosts:", config.servers())
    print ("Queues", config.queues("delta"))
    print ("Queues", config.queues("karst"))

    print(config.qstat("india"))
    print(config.qstat("india", user="*"))
    print(config.qstat("india", user="*", format="xml"))
    print(json.dumps(config.qstat("india", user="*", format="dict"), indent=4))
    print(config.username("bigred"))
