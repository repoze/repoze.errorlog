``repoze.errorlog``
===================

.. image:: https://travis-ci.org/repoze/repoze.errorlog.png?branch=master
        :target: https://travis-ci.org/repoze/repoze.errorlog

.. image:: https://readthedocs.org/projects/repozeerrorlog/badge/?version=latest
        :target: http://repozeerrorlog.readthedocs.org/en/latest/
        :alt: Documentation Status

This package implements a `WSGI <https://www.python.org/dev/peps/pep-0333/>`_
middleware filter which intercepts exceptions and writes them to a Python
logging module channel (or the ``wsgi.errors`` filehandle, if no channel is
configured).  It also allows the browsing of limited exception history via
a browser UI.

Please see ``docs/index.rst`` or http://repozeerrorlog.rtfd.org/ for
detailed documentation.
