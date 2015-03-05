from __future__ import print_function
import glob
import os.path
import shutil
from cloudmesh_base.Shell import Shell
from cloudmesh_pbs.api.ssh_config import ssh_config

def xcopy(src_dir, dest_dir, pattern, force=True):
    """copies all files matching a glob pattern such as *.yaml from
    the source to the destination directory if the file is not already
    in the directory in case force is set to Tru. If force is set to
    False, the file will not be copied if it already exists"""

    _src_dir = os.path.expanduser(src_dir)
    _dest_dir = os.path.expanduser(dest_dir)

    for file in glob.glob(os.path.join(_src_dir, pattern)):
        if force or file not in glob.glob(os.path.join(_src_dir, pattern)):
            print("Copy file {0} -> {1}".format(file, _dest_dir))
            shutil.copy(file, _dest_dir)
        else:
            print("Warning: {0} exists in {1}. "
                  "Ignoring copy.".format(file,
                                          os.path.join(os.path.split(_dest_dir)[-2:])))

def xmkdir(host, path):
    try:
        hosts = ssh_config()
        r = hosts.execute(host, "mkdir -p {0}".format(path))
        print (r)
    except Exception as e:
        print (e)
        

