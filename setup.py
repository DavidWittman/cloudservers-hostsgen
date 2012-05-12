#!/usr/bin/env python

from setuptools import setup, find_packages

__author__ = "David Wittman <david@wittman.com>"
NAME = "cloudservers-hostsgen"
DESC = "Auto-generates /etc/hosts for Rackspace Cloud Servers"
VERSION = "0.1"
REQS = [ 'python-novaclient==2.6.0' ]

setup(name = NAME,
      description = DESC,
      version = VERSION,  
      author = "David Wittman",
      author_email = "david@wittman.com",
      license = "BSD",
      install_requires = REQS,
      py_modules = ['hostsgen'],
      entry_points = """
        [console_scripts]
        cloudservers-hostsgen = hostsgen:main
        """
     )
