##############################################################################
#
# Copyright (c) 2007-2010 Agendaless Consulting and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the BSD-like license at
# http://www.repoze.org/LICENSE.txt.  A copy of the license should accompany
# this distribution.  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL
# EXPRESS OR IMPLIED WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND
# FITNESS FOR A PARTICULAR PURPOSE
#
##############################################################################

__version__ = '0.9.1'

import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

REQUIREMENTS = [
     'meld3',
     'Paste',
     ]

# elementtree is only required before Python 2.5.  The dependency is
# not caused by ourselves but by meld3, which fails to declare it.
if sys.version_info[:3] < (2,5,0):
    REQUIREMENTS.append('elementtree')

setup(name='repoze.errorlog',
      version=__version__,
      description='Error logging and reporting middleware',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware",
        ],
      keywords='web application server wsgi zope',
      author="Agendaless Consulting",
      author_email="repoze-dev@lists.repoze.org",
      url="http://www.repoze.org",
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['repoze'],
      zip_safe=False,
      tests_require = REQUIREMENTS,
      install_requires = REQUIREMENTS,
      test_suite="repoze.errorlog.tests",
      entry_points = """\
      [paste.filter_app_factory]
      errorlog = repoze.errorlog:make_errorlog
      """
      )

