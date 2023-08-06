#!/usr/bin/env python3
import os
from setuptools import setup, find_packages
#from notifator.version import __version__

#-----------problematic------
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

#exec(open('version.py').read())
#import codecs
import os.path

def readver(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()

def get_version(rel_path):
    for line in readver(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")

setup(
    name="notifator",
    description="Automatically created environment for python package",
    author="jaromrax",
    author_email="jaromrax@gmail.com",
    license="GPL2",
#    version=__version__,
    version=get_version("notifator/version.py"),
    #packages=find_packages(),
    packages=['notifator'],
    package_data={'notifator': ['data/*']},
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    scripts = ['bin/notifator', 'bin/checkbtrfs', 'bin/login-notify.py', 'bin/teleg_bot.py'],
    install_requires = ['gtts','fire','pydub','notify2']
)
#
#   To RECOVER AND ACCESS THE Data later in module: :
#  X DATA_PATH = pkg_resources.resource_filename('notifator', 'data/')
#  X DB_FILE =   pkg_resources.resource_filename('notifator', 'data/file')
#   DB_FILE = pkg_resources.resource_filename(
#       pkg_resources.Requirement.parse('nuphy2'),
#       'data/nubase2016.txt'
#   )
#   pip install -e .
#   bumpversion patch minor major release
#      release needed for pypi
