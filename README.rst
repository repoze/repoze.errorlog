``repoze.errorlog``
===================

This package implements a `WSGI <https://www.python.org/dev/peps/pep-0333/>`_
middleware filter which intercepts exceptions and writes them to a Python
logging module channel (or the ``wsgi.errors`` filehandle, if no channel is
configured).  It also allows the browsing of limited exception history via
a browser UI.

Please see ``docs/index.rst`` or http://repozeerrorlog.rtfd.org/ for
detailed documentation.
