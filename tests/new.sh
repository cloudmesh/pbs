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


