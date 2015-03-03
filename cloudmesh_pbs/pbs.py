from __future__ import print_function
from cloudmesh_base.ConfigDict import ConfigDict
from cloudmesh_install import config_file
from cloudmesh_pbs.api.xshellutil import xcopy, xmkdir
from cloudmesh.shell.Shell import Shell
from api.ssh_config import ssh_config
from xml.dom import minidom
import json
from string import Template
import os
from pprint import pprint

class PBS(object):

    id_file = "id.txt"
    
    def jobid_set(self, id):
        with open(self.id_file, "w") as text_file:
            text_file.write('%s' % id)
    
    def jobid_get(self):
        try:
            with open(self.id_file, "r") as f:
                content = f.read()
        except:
            self.jobid_set(0)
            content = 0
        self.id = content.strip()
        
        return self.id
    
    def jobid_incr(self):
        id = self.jobid_get()
        id = int(id)+1
        self.jobid_set(id)
        
    def load(self):
        self.filename = config_file("/cloudmesh_pbs.yaml")
        self.data = ConfigDict(filename=self.filename)
        self.hosts = ssh_config()

    def __init__(self, deploy=False):
        if deploy:
            self.deploy()
        self.load()
        self.id = self.jobid_get()
        
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
        server = pbs.data["cloudmesh"]["pbs"][server]
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

    def _write_to_file(self, script, filename):
        with open(filename, "w") as text_file:
            text_file.write('%s' % script)
    
    def qsub(self,  name, host, script, template=None, kind="dict"):
        self.jobid_incr()
        jobscript = self.create_script(name, script, template)
        
        # copy the script to the remote host
        self._write_to_file(jobscript, name)
        # copy script to remote host
        
        host = "india"
        remote_path = self.data.get("cloudmesh", "pbs", host, "scripts")
        
        print (remote_path)
        xmkdir(host, remote_path)
        
        # call qsub on the remot host
        r = Shell.scp("-v", name, host +":" + remote_path)        
        jobid = Shell.ssh(host, "qsub {0}/{1}".format(remote_path, name)).rstrip()
        
        
        qstat_xml_data = Shell.ssh(host, "qstat", "-x",  jobid).rstrip() 
            
        if kind == 'xml':
            r = qstat_xml_data
        else:    
            r = self.qstat_xml_to_dict(qstat_xml_data)
            r[unicode(jobid)][u"cm_jobid"] = self.jobid_get() 
        if kind == 'yaml':
            r = yaml.dump(r, default_flow_style=False)
        return r

    def variable_list(self, data):
        key = data.keys()[0]
        var_list = data[key]['Variable_List'].split(',')
        d = {}
        for element in var_list:
            (attribute, value) = element.split('=')
            d[attribute] = value
        
        return d
         
        
    def create_script(self, name, script, template=None):
        if template is None:
            template_script = script        
        data = {}
        data['script'] = script
        data['name'] = name
        
        result = template.format(**data)
        return result
    
    def read_script(self, filename, user=None, host='localhost'):
        if host in ['localhost'] and user is None:
            with file(filename) as f:
                content = f.read()
        else:
            # TODO: copy file from remote host
            print ("ERROR: not implemented")
            pass

        return content
            
if __name__ == "__main__":

    pbs = PBS(deploy=True)

    print(pbs)

    script_template = pbs.read_script("etc/job.pbs")
    print (script_template)
    
    script = """
    uname -a
    """
    
    jobname = "job-" + pbs.jobid_get()
    job_script = pbs.create_script(jobname, script, script_template)
    
    print(job_script)

    # xmkdir("india", "~/scripts/test")
    
    
    print(pbs.jobid_get())
    pbs.jobid_set(100)
    print(pbs.jobid_get())
    pbs.jobid_incr()
    
    
    
    jobname = "job-" + pbs.jobid_get() + ".pbs"
    r = pbs.qsub(jobname, "india", 'echo "Hello"', template=script_template)
    pprint(r)
    pprint(pbs.variable_list(r))
    
    #os.system ("cat " + jobname)
    print()
    
    '''
    print("Hosts:", pbs.servers())
    print ("Queues", pbs.queues("delta"))
    print ("Queues", pbs.queues("karst"))

    print(pbs.qstat("india"))
    print(pbs.qstat("india", user="*"))
    print(pbs.qstat("india", user="*", format="xml"))
    print(json.dumps(pbs.qstat("india", user="*", format="dict"), indent=4))
    print(pbs.username("bigred"))
    '''
