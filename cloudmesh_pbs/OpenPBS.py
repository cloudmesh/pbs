from __future__ import print_function

from pprint import pprint
from xml.dom import minidom

import yaml
from cloudmesh_base.Shell import Shell
from cloudmesh_base.ConfigDict import ConfigDict
from cloudmesh_base.util import banner
from cloudmesh_base.util import path_expand
from cloudmesh_base.locations import config_file
from cloudmesh_base.xshellutil import xcopy, xmkdir
from cloudmesh_base.ssh_config import ssh_config


class OpenPBS(object):
    id_file = "id.txt"

    def __init__(self, deploy=False):
        if deploy:
            self.deploy()
        self.load()
        self.id = self.jobid

    # #################################################################
    # JOB ID COUNTER
    # #################################################################

    def _load_jobid(self):
        try:
            with open(self.id_file, "r") as f:
                content = f.read()
        except:
            self.jobid = 0
            content = 0
        self.id = content.strip()
        return self.id

    def _write_jobid(self, id):
        with open(self.id_file, "w") as text_file:
            text_file.write('%s' % id)

    @property
    def jobid(self):
        return self._load_jobid()

    @jobid.setter
    def jobid(self, value):
        self._write_jobid(value)

    def jobid_incr(self):
        id = self.jobid
        id = int(id) + 1
        self.jobid = id

    def load(self):
        self.filename = config_file("/cloudmesh_pbs.yaml")
        self.data = ConfigDict(filename=self.filename)
        self.hosts = ssh_config()

    # ###################
    # GET DATA
    # ###################

    def __str__(self):
        return self.data.json()

    def servers(self):
        return self.data["cloudmesh"]["pbs"].keys()

    def queues(self, server):
        server = pbs.data["cloudmesh"]["pbs"][server]
        if "queues" in server:
            return server["queues"]
        else:
            return None

    def deploy(self, force=True):
        """copies the yal file from etc in the distribution to the .cloudmesh
        directory. If the file exits it will not be copied and a warning is
        thrown. If the file is the same as in etc no warning is thrown.
        """
        xcopy("../etc/", "~/.cloudmesh", "*.yaml", force=force)

    #
    # QSTAT
    #

    @classmethod
    def qstat_xml_to_dict(cls, xmldata):
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

    def qstat(self, host, user=True, format='dict'):
        data = None
        username = self.username(host)
        manager_host = self.manager(host)
        xml_data = Shell.ssh(manager_host, "qstat", "-x").rstrip()

        if format == 'dict':
            data = OpenPBS.qstat_xml_to_dict(xml_data)
            selected_data = {}
            for jobid in data:
                (owner, cm_host) = data[jobid]['Job_Owner'].split('@')
                if not user:
                    selected_data[unicode(jobid)] = data[unicode(jobid)]
                elif owner == username:
                    selected_data[unicode(jobid)] = data[unicode(jobid)]
            data = selected_data
            for jobid in data:
                data[unicode(jobid)][u"cm_jobid"] = jobid
                if "Variable_list" in data[unicode(jobid)]:
                    data[unicode(jobid)][u"cm_Variable_list"] = self.variable_list(data, jobid)
        elif format == "xml":
            if user is not None:
                print("WARNING: "
                      "restrictiong xml data for a user not supported.")
            data = xml_data
        return dict(data)

    def username(self, host):
        return self.hosts.username(host)

    def manager(self, host):
        try:
            m = self.data.get("cloudmesh", "pbs", host, "manager")
        except:
            print ("WARNING: Manager not defined for", host)
            print ("         Using the host")
            m = host
        return m

    def database_filename(self):
        return path_expand(self.data.get("cloudmesh", "pbsdatabase", "filename"))

    def _write_to_file(self, script, filename):
        with open(filename, "w") as text_file:
            text_file.write('%s' % script)

    def db_jobstatus(self, host, jobid, kind='dict'):
        return {}

    def jobstatus(self, host, jobid, kind='dict'):
        manager_host = self.manager(host)
        qstat_xml_data = Shell.ssh(manager_host, "qstat", "-x", jobid).rstrip()

        if kind == 'xml':
            r = qstat_xml_data
        else:
            r = self.qstat_xml_to_dict(qstat_xml_data)
            r[unicode(jobid)][u"cm_jobid"] = self.jobid
            r[unicode(jobid)]["cm_Variable_list"] = self.variable_list(r)
        if kind == 'yaml':
            r = yaml.dump(r, default_flow_style=False)
        return r

    @classmethod
    def list(cls, data, attributes):
        content = {}
        for jobid in data:
            content[jobid] = {}
            for attribute in attributes:
                try:
                    content[jobid][attribute] = data[jobid][attribute]
                except:
                    content[jobid][attribute] = "None"
        return content

    def qsub(self, name, host, script, template=None, kind="dict"):
        self.jobid_incr()
        jobscript = self.create_script(name, script, template)

        # copy the script to the remote host
        self._write_to_file(jobscript, name)
        # copy script to remote host

        remote_path = self.data.get("cloudmesh", "pbs", host, "scripts")

        print(remote_path)
        xmkdir(host, remote_path)

        manager_host = self.manager(host)

        # call qsub on the remot host
        r = Shell.scp(name, manager_host + ":" + remote_path)
        jobid = Shell.ssh(manager_host, "qsub {0}/{1}".format(remote_path, name)).rstrip()

        return self.jobstatus(host, jobid, kind=kind)

    def getid(self, data):
        key = data.keys()[0]
        return key

    @classmethod
    def variable_list(cls, data, id=None):
        if id is None:
            key = data.keys()[0]
        else:
            key = id
        var_list = data[key]['Variable_List'].split(',')
        d = {}
        for element in var_list:
            (attribute, value) = element.split('=')
            d[attribute] = value

        return d

    def create_script(self, name, script, template=None):
        # BUG
        if template is None:
            template_script = script
        data = {'script': script, 'name': name}

        result = template.format(**data)
        return result

    def read_script(self, filename, user=None, host='localhost'):
        if host in ['localhost'] and user is None:
            with file(filename) as f:
                content = f.read()
        else:
            # TODO: copy file from remote host
            print("ERROR: not implemented")
            pass

        return content


if __name__ == "__main__":
    # TODO: when hosts are bravo, echo, delta, the manager need sto be used to ssh

    host = "india"

    pbs = OpenPBS(deploy=True)
    manager = pbs.manager(host)
    xmkdir(manager, "~/scripts/test")

    print(pbs)

    script_template = pbs.read_script("etc/job.pbs")
    print(script_template)

    script = """
    uname -a
    """

    jobname = "job-" + pbs.jobid
    job_script = pbs.create_script(jobname, script, script_template)

    print(job_script)

    # print(pbs.jobid)
    # pbs.jobid_set(100)
    # print(pbs.jobid)
    pbs.jobid_incr()

    banner('qsub')

    jobname = "job-" + pbs.jobid + ".pbs"
    r = pbs.qsub(jobname, host, 'echo "Hello"', template=script_template)
    pprint(r)
    banner('variable list')
    pprint(OpenPBS.variable_list(r))

    banner('status')
    jobid = pbs.getid(r)
    r = pbs.jobstatus(host, jobid)

    pprint(r)

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

    # pbs.db.update(host="india")
    # attributes = ["cm_jobid", "cm_host", "cm_user", "Job_Name", "job_state", "exit_status"]
    # banner("LIST")
    # print(pbs.db.list(attributes, output="csv"))

    # pprint (pbs.data)
    # banner("table")
    # print(pbs.db.list(attributes, output="table"))
    # banner("yaml")
    # print(pbs.db.list(attributes, output="yaml"))
    # banner("dict")
    # print(pbs.db.list(attributes, output="dict"))

    # print(print_format_dict(pbs.db.data, header=None, kind='table'))

    # print(pbs.db.list(attributes, output="dict"))
