Notes
=========

* finish this current code using shelve
  
* adding mongoengine support as database provider

* adding redundancy/ fault tolerance of database
* adding (secure) REST interface
* using rest interface to communicate between matlab and framework
* identify excel table user interface from matlab to control jobs
* adding testing framework
* create simulation framework, so we do not block queueing systems and
  waste valuable hours of compute time.
* create throttle for interfaces, identified by limitations of queues
  and realtime performance data
* integrate performance prediction framework that we can switch on and
  off
* use XSEDE resources ( I will get you accounts once we are further
  along)
* Identify how to extract the jobs from the scientific application
  (DIFFICULT, I will probably do that)
* Run the application on the jobs
* define the dependency framework as indicated in the mail bellow and
  build a search function that allows us to identify jobs that we must
  run and resources on which we run them
* integrate a mechanism to copy data to the compute servers
* make sure the program we have is tested on at least 3-5 supercomputers
* bonus: see if we can get also hadoop across the machines or something similar.

Management of millions of jobs on a distributed set of super computers
in support of large scale data analysis for arctic environmental
data. We anticipate about 1.5 million jobs. The shelve project was a
warmup to the, but we would develop an abstraction and a provider so
we could use mongo or some other data store. than we observe and
manage who the data is distributed. We would formulate a simple
description with

job1
 data:
	input:
	- file 1
	- file 2
      output:
      - file 3
      - file 4
 executable:
       http://github. …. /prg.sh


We envision that we can create all the 1.5 million jobs this way.
Than we can look for which input files are the same, and than load up
the calculation where the data is. The result would be integartied in
cloudmesh and you would become a contributor.
