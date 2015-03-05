Cloudmesh PBS
======================================================================

Cloudmesh PBS provides an easy mechanism to interface with queuing
systems. It is based on cloudmesh version 2 that uses separate packages
instead of one big cloudmesh package. The packages are named
cloudmesh_*, where * is a placeholder for the package names.

The advantage of cloudmesh_pbs is that it can start pbs jobs on remote
machines while using some simple templates. These jobs are entered in
a local database and their status on the remote machines can be
monitored. At this time we provide a simple API, but will soon add
also a command interface as well as a secure rest interface.

Project requirements:
----------------------------------------------------------------------

* cloudmesh_base
  
Instalation (pending)
----------------------------------------------------------------------

The easiest way to install cloudmesh PBS is with pip. We recommend
that you do it in a virtual environment. Once you have created and
activated a virtualenv you can install cloudmesh_pbs with the
following commands::

  pip install cmd3
  pip install cloudmesh_base
  pip install cloudmesh_database   (not yet needed in this release)
  pip install cloudmesh_pbs
  
Github repository
----------------------------------------------------------------------

The source code can be found at:

* https://github.com/cloudmesh/pbs

Usage
----------------------------------------------------------------------

Service Specification
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When dealing with remote services we often need to customize
interfaces and access. Instead of completely reinventing a
specification file, we are leveraging first the ssh config file for
the remote login to the servers that allow us to execute pbs
commands. Second we have defined a simple yaml file that allows us to
set up some service specific items. At this time it supports the
specification of jobs submitted through various supercomputers that
are either managed individually through queues, through groups of
queues that are managed for multiple machines in a single management
node.

SSH Config
~~~~~~~~~~~~~~~~~~~~~~~~

We assume that you have set up all machine in ssh config that you like
to access with a simple keyword. For example you like to access the
machine cluster.example.com. We also assume you have the username
albert on that machine.  In this case we assume you have set up a
simple ssh config such as::

  Host cluster
     Hostname cluster.example.com
     User albert

Naturally once you place your public key in the authorized_hosts files
on the cluster, you will be able to log into the machine with::

  ssh cluster

Naturally, you can try commands such as::

  ssh cluster uname -a

You should be able to also verify if you can execute the command qstat
with::

  ssh cluster qstat

If this all works you can specify a yaml file for cloudmesh_pbs. We
have included a sample yaml file in the etc directory of the source
code that you can modify accordingly. If we use the example you will
have::

  meta:
    yaml_version: 2.1
    kind: pbs
    cloudmesh:
      pbs:
        cluster:
          manager: cluster
          scripts: ~/qsub/india
          queues:
          - batch
          - long

This file is places in the directory ~/.cloudmesh

The important part of the file is in the cloudmesh - pbs portion. Here
the name of the machine that we used in .ssh/config is used,
e.g. cluster. The manager is specified to also be the machine
cluster. This is the machine on which the qsub and qstat commands are
executed for this machine. If the management node is different it can
be specified here. The scripts attribute specifies where the pbs
scripts are placed on the remote machine before they are submitted.
To add specific queues you simply can include them as a list in the
queues attribute

.. note:: queue management will be enhanced

API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The API to interface with the queues is straight forward and
documented in more details here::

  TBD

A simple example will show you how to submit a job and check upon its
status. First we define a default host::

    host = "india" 

Next we declare the pbs instance that we use to interact with the
various systems. Upon creation it reads the ssh config file and the
cloudmesh yaml file::

    pbs = PBS(deploy=True)

 Next we find the manager of the host that we use to copy and to
 initiate the pbs commands on::
    
    manager = pbs.manager(host)

let us create on that host the directory ~/scripts/test::
  
    xmkdir(manager, "~/scripts/test")

Now we need to create a pbs job script. For this we use a template that
we have in the etc directory::

    script_template = pbs.read_script("etc/job.pbs")

the template contains the ability to replace the script with some real
commands. Let us use the uname command::
  
    script = """
    uname -a
    """

Also we want to give the job a unique id. For that we maintain in pbs
an internal variable that will be increased every time we submit a
job. We do it here with the incr command::

    pbs.jobid_incr()
    jobname = "job-" + pbs.jobid_get()
    job_script = pbs.create_script(jobname, script, script_template)

Let us now submit the job to the given host::

    r = pbs.qsub(jobname, host, script, template=script_template)

it will return the information of the job. Optionally one can define
an output format (see the API) such as a dict or  a yaml
representation. To optain the PBS variable list as a dict we can use:: 

    d = pbs.variable_list(r)


Status of the job
~~~~~~~~~~~~~~~~~~~~~~~~

The status of a job can be obtained with::

  r = jobstatus(self, host, jobid)

It will not only include the status, but also the environment
variables the job is executed in. 
  

Termination of the Job
~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

Listing of all jobs
~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

Persistent Database
~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD

Cloudmesh integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

TBD
