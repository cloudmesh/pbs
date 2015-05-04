from __future__ import print_function

import os
import sys
from pprint import pprint
from xml.dom import minidom
from collections import Counter

import yaml
from cloudmesh_base.Shell import Shell
from cloudmesh_base.ConfigDict import ConfigDict
from cloudmesh_base.util import banner
from cloudmesh_base.util import path_expand
from cloudmesh_base.locations import config_file
from cloudmesh_base.xshellutil import xcopy, xmkdir
from cloudmesh_base.ssh_config import ssh_config

from cloudmesh_base.logger import LOGGER

log = LOGGER(__file__)

class OpenPBS(object):

    # #################################################################
    # INITIALIZATION
    # #################################################################

    def __init__(self, deploy=True, yaml_filename="/cloudmesh_pbs.yaml"):
        """
        Creates an object instance of communication with pbs batch queues
        running on multiple hosts.

        It also is used to create some configuration parameters if deploy
        is set to True.

        it creates in the CLOUDMESH deploy directory the directory pbs and puts
        the dababse file pbs.db and the file that is used to store the current
        job number. The job number is shared among all resources and supposed
        to be unique.


        :param deploy: If True, creates the configuration files
        :param yaml_filename: The cloudmesh pbs yaml file. Defaults to
                              cloudmesh_pbs.yaml
        :return: an object instance of OpenPBS
        """
        self.yaml_filename = config_file(yaml_filename)

        self.pbs_dir = config_file("/pbs")
        self.id_file = config_file("/pbs/id.txt")
        self.db_file = config_file("/pbs/pbs.db")

        if deploy:
            self.deploy()
        self.load()
        self.id = self.jobid

        self.pbs_nodes_data = None

    def info(self):
        """
        Prints some elementary information about the configuration of the
        OpenPBS instance.

        :return:
        """
        print("{:>20} = {:}".format("Config Dir", self.pbs_dir))
        print("{:>20} = {:}".format("Job ID file", self.id_file))
        print("{:>20} = {:}".format("Db file", self.db_file))

    def load(self, yaml_filename=None):
        """
        Loads the cloudmesh pbs yaml file.

        :param yaml_filename: The filename of the yaml file
        """
        log.debug("PBS yaml filename: {0}".format(self.yaml_filename))
        if yaml_filename is None:
            yaml_filename = self.yaml_filename
        else:
            self.yaml_filename = config_file(yaml_filename)
        self.data = ConfigDict(filename=self.yaml_filename)
        self.hosts = ssh_config()

    def deploy(self, force=True):
        """
        Copies the yaml file from etc in the distribution to the .cloudmesh
        directory. If the file exits it will not be copied and a warning is
        thrown. If the file is the same as in etc no warning is thrown.

        :param force: Forgot what this does, please document.
        """
        # setup ~/.cloudmesh/pbs
        log.debug(self.pbs_dir)
        if not os.path.isdir(self.pbs_dir):
            os.makedirs(self.pbs_dir)

        self._load_jobid()

        xcopy("../etc/", config_file(""), "*.yaml", force=force)

    # #################################################################
    # JOB ID COUNTER
    # #################################################################

    def _load_jobid(self):
        """
        internal method that loads the job id from the job id file.

        :return: the string of the job id
        """
        try:
            with open(self.id_file, "r") as f:
                content = f.read()
            self.id = content.strip()
        except:
            self.jobid = 0

        return self.id

    def _write_jobid(self, id):
        """
        Internal method that overwrites the job id to the specified id.

        :param id:  the job id
        :return: the string of the id
        """
        log.debug("CCC:" + self.id_file)
        if not os.path.isfile(self.id_file):
            open('file', 'w').close()
        with open(self.id_file, "w+") as text_file:
            text_file.write('%s' % id)
        return id

    @property
    def jobid(self):
        """
        The job id
        :return: The string of the job id
        """
        return self._load_jobid()

    @jobid.setter
    def jobid(self, value):
        """
        sets the job id to the given value
        :param value: The value of the jobid
        """
        self._write_jobid(value)

    def jobid_incr(self):
        """
        increments the job id by 1
        """
        id = self.jobid
        id = int(id) + 1
        self.jobid = id


    # ###################
    # GET DATA
    # ###################

    def __str__(self):
        """
        Returns the json object of the dict as string
        NOTE: should probably use json.dumps
        :return: the string representation of teh job data
        """
        return self.data.json()

    def servers(self):
        """
        List of the servers as defined in the .ssh/config file as dict
        :return: the dict representing the servers
        """
        return self.data["cloudmesh"]["pbs"].keys()

    def queues(self, server):
        """
        List the queues dict of the given server
        :param server:
        :return:
        """
        server = pbs.data["cloudmesh"]["pbs"][server]
        if "queues" in server:
            return server["queues"]
        else:
            return None


    #
    # QSTAT
    #

    @classmethod
    def qstat_xml_to_dict(cls, xmldata):
        """
        Internal method that converst a qsta xml representation to a dict.
        :param xmldata: The xml data from qstat -x
        :return: a dict representation of the data
        """
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
        """
        executes the qstat command on a particular host and returns
        the information as dict.

        :param host: The host as specified in ~/.ssh/config
        :param user:  If True, only retirns information for the user
                      If False, all jobs for all users are returned
        :param format:
        :return:
        """
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
        """
        The username of the host as specified in ~/.ssh/conf
        :param host: The name of the host
        :return: The username
        """
        return self.hosts.username(host)

    def manager(self, host):
        """
        In some cases a queue of another machine is hosted through a
        management node different from that machine. The manager command
        allows us to specify on which machine the qstat command is issued.

        :param host: The name of the host
        :return: The name of the management host
        """
        try:
            m = self.data.get("cloudmesh", "pbs", host, "manager")
        except:
            print ("WARNING: Manager not defined for", host)
            print ("         Using the host")
            m = host
        return m

    def database_filename(self):
        """
        The name of the database file
        :return:
        """
        return path_expand(self.data.get("cloudmesh", "pbsdatabase", "filename"))

    def _write_to_file(self, script, filename):
        """
        Internal function to write a pbs script to a file
        :param script: content of the script
        :param filename: filename
        """
        with open(filename, "w") as text_file:
            text_file.write('%s' % script)

    def db_jobstatus(self, host, jobid, kind='dict'):
        """This method is not yet implemented"""
        return {}

    def jobstatus(self, host, jobid, kind='dict'):
        """
        The status of a specific job

        :param host: The host on which the job is running
        :param jobid: The jobid as specified by the queing system
        :param kind: The output can be returned as dict, xml, and yaml
        :return:
        """

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
        """
        Internal function to lists the information in the data dict
        :param data: The data directory
        :param attributes: the attribute to return
        :return: the content found for he specified attribute
        """
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
        """
        Executes the qsub command on a given host.
        NOTE this method may not yet be fully implemented

        :param name: name of the script
        :param host: host on which the script is to be run
        :param script: The name of the script
        :param template: The script is wrapped into a template
        :param kind: The return is passed as dict, yaml, xml
        :return:
        """
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
        """
        Internal function to list the variables of a qstat job
        which is 'Variable_List'

        :param data: The input data value
        :param id: The id of the job
        :return:
        """
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

    def anodes(self, host, refresh=True):
        pass


    def nodes(self, host, refresh=True):
        """
        returns the information from the command pbsnodes in a dict.

        :param host: the name of the host as specified in the .ssh/config file
        :param refresh: if False, reads returns a cached value
                        if True, issues a new command and refreshes the cach
        :return: information of the pbsnodes command in a dict
        """

        manager_host = self.manager(host)
        if self.pbs_nodes_data is None or refresh:
            try:
                result = Shell.ssh(manager_host, "pbsnodes", "-a")
            except:
                raise RuntimeError(
                    "can not execute pbs nodes on host {0}".format(manager_host))
            pbsinfo = {}
            nodes = result.split("\n\n")
            for node in nodes:
                pbs_data = node.split("\n")
                pbs_data = [e.strip() for e in pbs_data]
                name = pbs_data[0]
                if name != "":
                    pbsinfo[name] = {u'name': name}
                    for element in pbs_data[1:]:
                        try:
                            (attribute, value) = element.split(" = ")
                            if attribute == 'status':
                                status_elements = value.split(",")
                                pbsinfo[name][attribute] = {}
                                for e in status_elements:
                                    (a, v) = e.split("=")
                                    pbsinfo[name][attribute][a] = v
                            elif attribute == 'jobs':
                                pbsinfo[name][attribute] = value.split(',')
                            elif attribute == 'note' and (
                                        value.strip().startswith("{") or value.strip().startswith("[")):
                                pbsinfo[name][attribute] = literal_eval(value)
                            else:
                                pbsinfo[name][attribute] = value
                        except:
                            pass
            self.pbs_nodes_data = pbsinfo

        return self.pbs_nodes_data

    def nodes_sum(self, host):
        sum = 0
        distribution = self.nodes_distribution(host)
        for key in distribution:
            i = int(distribution[key])
            sum = sum + i
        return sum

    def nodes_distribution(self, host):
        """prints the distribution of services"""

        manager_host = self.manager(host)

        def pbsnodes_data(manager_host):
            result = str(
                Shell.ssh(manager_host, "pbsnodes", "-l", "-n"))[:-1]
            return result


        empty = ["", "", ""]
        x = [x.split() for x in pbsnodes_data(manager_host).split("\n")]

        # Fill missing values

        r = []
        for line in x:
            new = ["unkown", "unkown", "unkown"]
            for i in range(0, len(line)):
                try:
                    new[i] = line[i]
                except:
                    pass
            r.append(new)

        # just taking column 2

        x = [x[2] for x in r]

        # print "GFKHFJH ", x
        cnt = Counter(x)

        # print "COUNT",

        result = dict(cnt)

        return result


if __name__ == "__main__":
    # TODO: when hosts are bravo, echo, delta, the manager need sto be used to ssh

    host = "india"

    pbs = OpenPBS(deploy=True)




    manager = pbs.manager(host)

    pprint (pbs.nodes(host))

    pprint (pbs.nodes_distribution(host))

    pprint (pbs.nodes_sum(host))
    sys.exit()

    pbs.info()


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
