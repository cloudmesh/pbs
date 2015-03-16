#! /bin/sh

cd ~
deactivate
rm -rf TEST
virtualenv TEST -p /usr/local/bin/python
source ~/TEST/bin/activate
which python
pip install cmd3
pip install cloudmesh_base
pip install cloudmesh_database
echo "######################################################################"
echo "Running tests"
echo "######################################################################"

mkdir ~/NOSETESTS

cd ~/NOSETESTS
#
# git clone git@github.com:cloudmesh/cmd3.git
# 
#

cd ~/NOSETESTS
git clone git@github.com:cloudmesh/pbs.git
cd pbs/tests

nosetests --nocapture -v database.py
nosetests --nocapture -v submit.py
