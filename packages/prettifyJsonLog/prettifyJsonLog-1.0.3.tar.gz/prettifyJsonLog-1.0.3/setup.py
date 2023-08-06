#!/usr/bin/env python

import os
from setuptools import setup, find_packages


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

setup(name='prettifyJsonLog',
      description='A small python programm to make json log formats human readable',
      long_description=README,
      long_description_content_type="text/markdown",
      url="https://github.com/neumantm/prettifyJsonLog",
      license="MIT",
      author='Tim Neumann',
      author_email='neuamntm@fius.informatik.uni-stuttgart.de',

      setup_requires=[
        "setuptools_scm"
      ],
      use_scm_version=True,
      include_package_data=True,
      packages=find_packages(),
      entry_points = {
          'console_scripts': ['prettifyJsonLog=prettifyJsonLog.prettifyJsonLog:main'],
      }
     )
