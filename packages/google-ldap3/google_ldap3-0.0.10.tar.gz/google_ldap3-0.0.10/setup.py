"""
"""

# Created on 2013.07.11
#
# Author: Giovanni Cannata
#
# Copyright 2013 - 2018 Giovanni Cannata
#
# This file is part of google_ldap3.
# google_ldap3 is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# google_ldap3 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with google_ldap3 in the COPYING and COPYING.LESSER files.
# If not, see <http://www.gnu.org/licenses/>.

import os
import glob
import shutil
from json import load
from distutils.command.clean import clean
from distutils import log
from setuptools import setup

# {
#     "package_folder": ".",
#     "email": "yshan20@su.edu",
#     "package_name": "google-google_ldap3",
#     "url": "https://github.com/462548187/google-ldap3.git",
#     "description": "A strictly RFC 4510 conforming LDAP V3 pure Python client library",
#     "author": "Leo",
#     "version": "0.0.5",
#     "license": "LGPL v3"
# }

version = "0.0.10"
author = "Leo"
email = "yshan20@su.edu"
license = "LGPL v3"
url = "https://github.com/462548187/google-ldap3.git"
description = ""
package_name = "google_ldap3"
package_folder = "."

long_description = str(open('README.rst').read())
packages = ['google_ldap3',
            'google_ldap3.abstract',
            'google_ldap3.core',
            'google_ldap3.operation',
            'google_ldap3.protocol',
            'google_ldap3.protocol.sasl',
            'google_ldap3.protocol.schemas',
            'google_ldap3.protocol.formatters',
            'google_ldap3.strategy',
            'google_ldap3.utils',
            'google_ldap3.extend',
            'google_ldap3.extend.novell',
            'google_ldap3.extend.microsoft',
            'google_ldap3.extend.standard',
            ]

setup_kwargs = {'packages': packages,
                'package_dir': {'': package_folder}}


class Clean(clean):
    def run(self):
        clean.run(self)
        # Let's clean compiled *.py[c,o] *.c *.so
        for subdir in ('google_ldap3',):
            root = os.path.join(os.path.dirname(__file__), subdir)
            for dirname, dirs, _ in os.walk(root):
                for to_remove_filename in glob.glob('{0}/*.py[ocx]'.format(dirname)):
                    os.remove(to_remove_filename)
                for to_remove_filename in glob.glob('{0}/*.c'.format(dirname)):
                    os.remove(to_remove_filename)
                for to_remove_filename in glob.glob('{0}/*.so'.format(dirname)):
                    os.remove(to_remove_filename)
                for dir_ in dirs:
                    if dir_ == '__pycache__':
                        shutil.rmtree(os.path.join(dirname, dir_))


setup_kwargs['cmdclass'] = {'clean': Clean}

setup(name=package_name,
      version=version,
      install_requires=['pyasn1>=0.4.8'],
      license=license,
      author=author,
      author_email=email,
      description=description,
      long_description=long_description,
      keywords='python3 python2 ldap',
      url=url,
      classifiers=['Intended Audience :: Developers',
                   'Intended Audience :: System Administrators',
                   'Operating System :: MacOS :: MacOS X',
                   'Operating System :: Microsoft :: Windows',
                   'Operating System :: POSIX :: Linux',
                   'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2',
                   'Programming Language :: Python :: 3',
                   'Topic :: Software Development :: Libraries :: Python Modules',
                   'Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP'],
      **setup_kwargs
      )
