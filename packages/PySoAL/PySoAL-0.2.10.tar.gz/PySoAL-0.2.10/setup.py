# -*- coding: utf-8 -*-
#  Copyright (c) 2021. Institute for High Voltage Equipment and Grids, Digitalization and Power Economics (IAEW)
#  RWTH Aachen University
#  Contact: Thomas Offergeld (t.offergeld@iaew.rwth-aachen.de)
#  #
#  This module is part of PySoAL.
#  #
#  PySoAL is licensed under the BSD-3-Clause license.
#  For further information see LICENSE in the project's root directory.

from setuptools import setup, find_packages

from os import path
here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

classifiers = [
    'Programming Language :: Python',
    'Programming Language :: Python :: 3']

setup(
    name='PySoAL',
    version='0.2.10',
    author='Thomas Offergeld',
    author_email='t.offergeld@iaew.rwth-aachen.de',
    description='Solver abstraction layer for power system optimization',

    install_requires=["numpy", "gurobipy"],
    extras_require={
                    "test": ["pytest", "pytest-xdist"]},
    packages=find_packages(),
    include_package_data=True,
    classifiers=classifiers,
    long_description=long_description,
    long_description_content_type='text/markdown'
)
