TODO
=====

This page contains a summary of tasks to be done with people assignments to do them
It also includes anticipated deadlines

Task 1: [DONE] finish the yaml pluging command.
    priority: high
    Who: Gregor
    Date: 22 May, 2015
    Status: completd. The implementation is now in cmd3

       cm plugin add ..
       cm plugin delete ..

    Description: cmd3 contains a cmd3.yaml file that can be created with
    cm setup_yaml. However we do not have a method that easily adds a new
    plugin to the yaml file or lists the plugins that are defined in the
    yaml file

Task 2: implement the server commands of cm_shell_job.py
    priority: high
    Who: Ryan, Gregor
    Date:

    This includes start, stop, kill, clean, and stat and deploy
    Please note that the logic is mostly implemented in cm_jobdb.py

    when implementing the job command, make sure the database is declared as
    part of the do_job command. you make need to be careful naming your
    database and collection as this class is a mixin and it may overwrite
    other databases.

    we suggest to use the name self.hpc_jobdb as a prefix as we know its
    not used by other cloudmesh commands.

Task 3: implement and test logic for modifying a job object in the database
    priority: high
    Who: Ryan
    Date:

Task 4: implement a simple statistic of the database showing jobs in states
    priority: high
    Who: Ryan
    Date:

Task 5: use of hostlist for defining jobs
    priority: high
    Who: Drew, Gregor did the hostlist portion
    Date:
    the input and out put may include multiple files of similar syntax
    we like to modify the code to use multiple files, and also make sure we
    can use hostlist for specifying them. This needs to be implemented at cm
    command and as API that is called by the cm command
    
        cm job add job[1-100] --input=a[1-100],b[101-200] --output=c[1-100],d[1-100],e[1-100]
        
    creates 100 jobs with univqe gob names
    
        cm job delete job[1-100] deletes the appropriate jobs

Task 5.a: complede the job command
    priority: high
    Who: Drew, Gregor did the docopt (in part)
    Date:

    complete the docops and the call to the methods Ryan defined. If
    methods are missing communicate with Ryan

	
Task 6: REST service for client commands
    priority: medium
    Who:
    Date:
    so far we just implemented a client server model. We will in the next task
    replace the backend API implementations with rest calls so that a server is
    contacted and the client can be installed without dependcies.
    We assume that a configuration file such as cloudmesh_pbs.yaml
    includes the endpoint for the rest service. Insetead of just overwriting the existing
    api we want to write a new one and introduce a provider model that allows us to switch
    between the c2 -tier and the rest model

    before implementation, make proposal.

    take a look at whet is done for 5. look at the commands replace
    most " " cleverly with / and you have routes

    fore example

    /job/add/<name>/....
    /job/delete/<name>/...

    figure out how options/arguments should be passed

    you can use flask restful
    or python eve/flask eve
    
Task 6: performance study
    priority: low
    Who:
    Date:
    utilize the cm command and the hostlist feature to create lots of jobs and test
    performance of creation and inclusion, contrast the performance

