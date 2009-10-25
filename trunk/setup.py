#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2009 Bryan Davis <bender@punkdev.com>
# All rights reserved.
# $Id$
"""
"""

import ez_setup
ez_setup.use_setuptools()
from setuptools import setup, find_packages

__version__ = '1.0.0'

setup(
    name="stattrap",
    version=__version__,
    packages=["stattrap",],
    install_requires=['docutils>=0.3'],
    setup_requires=['nose>=0.11'],
    package_data = {
      '': ['*.txt', '*.rst'],
    },
    test_suite='nose.collector',
    
    author = "Bryan Davis",
    author_email = "bender@punkdev.com",
    description = "Track application use statistics",
    license = "GPL",
)
