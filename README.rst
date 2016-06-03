repoze.errorlog
===============

.. image:: https://travis-ci.org/repoze/repoze.errorlog.png?branch=master
        :target: https://travis-ci.org/repoze/repoze.errorlog

.. image:: https://readthedocs.org/projects/repozeerrorlog/badge/?version=latest
        :target: http://repozeerrorlog.readthedocs.org/en/latest/
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/repoze.errorlog.svg
        :target: https://pypi.python.org/pypi/repoze.errorlog

.. image:: https://img.shields.io/pypi/pyversions/repoze.errorlog.svg
        :target: https://pypi.python.org/pypi/repoze.errorlog

This package implements a `WSGI <https://www.python.org/dev/peps/pep-0333/>`_
middleware filter which intercepts exceptions and writes them to a Python
logging module channel (or the ``wsgi.errors`` filehandle, if no channel is
configured).  It also allows the browsing of limited exception history via
a browser UI.

Installation
------------

Install using setuptools, e.g. (within a virtualenv)::

 $ easy_install repoze.errorlog

or using pip::

 $ pip install repoze.errorlog


Usage
-----

For details on using the various components, please see the
documentation in ``docs/index.rst``.  A rendered version of that documentation
is also available online:

 - http://repozeerrorlog.readthedocs.org/en/latest/


Reporting Bugs 
--------------

Please report bugs in this package to

  https://github.com/repoze/repoze.errorlog/issues


Obtaining Source Code
---------------------

Download development or tagged versions of the software by visiting:

  https://github.com/repoze/repoze.errorlog

