#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from jsontp.__init__ import __version__

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()


setup(
  name='jsontp',
  version=__version__,
  description='JSON Tree Parser',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Nodiru Gaji',
  author_email='c0d3r.nodiru.gaji@gmail.com',
  url='https://github.com/ames0k0/jsontree',
  packages=['jsontp'],
  license='GNU General Public License v3 (GPLv3)',
  classifiers=[
    'Programming Language :: Python :: 3.10',
  ],
  platforms=[
    'Operating System :: OS Independent',
  ],
)
