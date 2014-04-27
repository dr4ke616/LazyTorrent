#!/usr/bin/env python

# Copyright (c) 2012 - 2014 Adam Drakeford <adamdrakeford@gmail.com>
# See LICENSE for details.

"""
Distutils installer for Lazy Torrent.
"""

import sys
import json
if not hasattr(sys, "version_info") or sys.version_info < (2, 7):
    raise RuntimeError("Lazy Torrent requires Python 2.7 or later.")

from setuptools import setup, find_packages


def load_application():
    with open('config/application.json', 'r') as app:
        application = json.loads(app.read())

    return application


def get_application_version():

    return load_application()['version']


def get_application_name():

    return load_application()['name']


def get_application_description():

    return load_application()['description']


def load_requirements():
    with open('requirements/_base.txt', 'r') as req:
        requirements = req.read()

    return requirements.split('\n')


def load_dependencies():
    with open('requirements/_eggs.txt', 'r') as dep:
        dependencies = dep.read()

    return [
        dep[3:] for dep in dependencies.split('\n')
        if not dep.startswith('#') and len(dep) > 0
    ]


setup(
    name=get_application_name(),
    version=get_application_version(),
    description=get_application_description(),
    author='Adam Drakeford',
    author_email='adamdrakeford@gmail.com',
    license='GPL',
    download_url='https://bitbucket.org/dr4ke616/auto_torrent_downlaoder.git',
    packages=find_packages(),
    install_requires=load_requirements(),
    dependency_links=load_dependencies(),
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Development Status :: 1 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Twisted',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
    ]
)
