# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 13:24:42 2020

@author: Peter
"""

from __future__ import print_function
from setuptools import setup, find_packages
import sys

setup(
    name="siat",
    version="1.0.1",
    author="WANG Dehong (Peter)",
    author_email="wdehong2000@163.com",
    description="Security Investment Analysis Tools",
    long_description=open("README.rst").read(),
    license="WANG Dehong",
    packages=['siat'],
    classifiers=[
        "Environment :: Anaconda Environment",
        'Intended Audience :: Financial Researchers',
        'License :: OSI Approved :: BFSU License',
        'Natural Language :: Chinese/English',
        'Operating System :: Windows 7/10',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Topic :: Finance :: Analysis',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',        
    ],
    zip_safe=True,
)