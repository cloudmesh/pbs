#!/usr/bin/env python

import glob
import os

from cloudmesh_base.util import banner
from setuptools import setup, find_packages
from setuptools.command.install import install


version = "2.2.2"

requirements =     [
        'cloudmesh_base',             
        'sh',
        'docopt',
        'pyaml',
        'simplejson',
        'nose',
        'cmd3',
    ]


# try:
#     from fabric.api import local
# except:
#     os.system("pip install fabric")
#     from fabric.api import local

home = os.path.expanduser("~")


def auto_create_version():
    with open("cloudmesh_pbs/__init__.py", "r") as f:
        content = f.read()
    
    if content != 'version = "{0}"'.format(version):
        banner("Updating version to {0}".format(version))
        with open("cloudmesh_pbs/__init__.py", "w") as text_file:
            text_file.write('version="%s"' % version)

auto_create_version()

#
# AUTO-CREATE REQUIREMENTS FROM ARRAY
#
def auto_create_requirements():
    banner("Creating requirements.txt file")
    with open("requirements.txt", "r") as f:
        file_content = f.read()
        
    setup_requirements = '\n'.join(requirements)
    
    if setup_requirements != file_content:
        with open("requirements.txt", "w") as text_file:
            text_file.write(setup_requirements)


class CreateRequirementsFile(install):
    """Create the requiremnets file."""
    def run(self):    
        auto_create_requirements()
        
class UploadToPypi(install):
    """Upload the package to pypi."""
    def run(self):
        auto_create_version()
        os.system("Make clean Install")
        os.system("python setup.py install")                
        banner("Build Distribution")
        os.system("python setup.py sdist --format=bztar,zip upload")        

class RegisterWithPypi(install):
    """Upload the package to pypi."""
    def run(self):
        banner("Register with Pypi")
        os.system("python setup.py register")        

class InstallBase(install):
    """Install the package."""
    def run(self):
        auto_create_requirements()
        banner("Install Cloudmesh Base")
        install.run(self)

class InstallRequirements(install):
    """Install the requirements."""
    def run(self):
        banner("Install Cloudmesh Base Requirements")
        os.system("pip install -r requirements.txt")
        
class InstallAll(install):
    """Install requirements and the package."""
    def run(self):
        banner("Install Cloudmesh Base Requirements")
        os.system("pip install -r requirements.txt")
        banner("Install Cloudmesh Base")        
        install.run(self)

class CreateDoc(install):
    """Install requirements and the package."""
    def run(self):
        banner("Create Documentation")
        os.system("python setup.py install")
        os.system("sphinx-apidoc -o docs/source cloudmesh_pbs")
        os.system("cd docs; make -f Makefile html")

setup(
    name='cloudmesh_pbs',
    version=version,
    description='A simple pbs queue management framework for multiple supercomputers',
    # description-file =
    #    README.rst
    author='Cloudmesh Team',
    author_email='laszewski@gmail.com',
    url='http://github.org/cloudmesh/pbs',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering',
        'Topic :: System :: Clustering',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Boot',
        'Topic :: System :: Systems Administration',
        'Framework :: Flask',
        'Environment :: OpenStack',
    ],
    packages=find_packages(),
    include_package_data=True,
#    data_files=[
#        (home + '/.cloudmesh', [
#            'etc/FGLdapCacert.pem',
#            'etc/india-havana-cacert.pem',
#            'etc/cloudmesh_flavor.yaml']),
#        (home + '/.cloudmesh/etc', [
#            'etc/cloudmesh.yaml',
#            'etc/me-none.yaml',
#            'etc/cloudmesh.yaml',
#            'etc/cloudmesh_server.yaml',
#            'etc/cloudmesh_rack.yaml',
#            'etc/cloudmesh_celery.yaml',
#            'etc/cloudmesh_mac.yaml',
#            'etc/cloudmesh_flavor.yaml',
#            'etc/ipython_notebook_config.py']),
#    ],
#    entry_points={'console_scripts': [
#        'cm-cluster = cloudmesh.cluster.cm_shell_cluster:main',
#    ]},
    install_requires=requirements,
    cmdclass={
        'install': InstallBase,
        'requirements': InstallRequirements,
        'all': InstallAll,
        'pypi': UploadToPypi,
        'pypiregister': RegisterWithPypi, 
        'create_requirements': CreateRequirementsFile,
        'doc': CreateDoc,
        },
)

