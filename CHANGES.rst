Changelog
=========

1.1 (2016-06-03)
----------------

- Add support for Python 3.5.

- Drop support for Python 2.6 and 3.2.

1.0.0 (2015-02-07)
------------------

- Add support for Python 3.2, 3,3, and 3.4, and PyPy3.

- Drop dependency on ``Paste`` (forking / simplifying
  ``paste.request.parse_querystring`` and ``paste.request.construct_url``).

- Add support for testing on Travis.

- Add Sphinx documentation.

- Drop support for Python 2.4 / 2.5.

0.9.2 (2012-03-29)
------------------

- This release is the last which will maintain support for Python 2.4 /
  Python 2.5.

- Add support for continuous integration using ``tox`` and ``jenkins``.

- Add support for PyPy.

- Add 'setup.py dev' alias (runs ``setup.py develop`` plus installs
  ``nose`` and ``coverage``).

- Moved to github.

0.9.1 (2010-05-23)
------------------

- Make it possible to send exceptions to a logger channel as described
  in the docs; this didn't actually work previously because a) I'm not
  very good at programming and b) the Python logging module is
  terrible (using ``s[-1]`` and not catching an exception when the
  string is empty rather than using ``s.endswith()``, at least under
  Python 2.4).

0.9 (2010-05-23)
----------------

- Bump copyrights.

- Remove dependency on ``ez_setup.py``.

- Docs now show how to use ``ErrorLog`` outside PasteDeploy.

- Avoid a dependency on `elementtree` when used with Python 2.5 and later.
  In those Python versions we used the built-in ``xml.etree`` support.

- 100% test coverage.

0.8 (2008-06-25)
----------------

- Remove post-mortem debug middleware (moved to ``repoze.debug``).

- Initial PyPI release.

0.7 (2008-05-21)
----------------

- Add post-mortem debug middleware (``egg:repoze.errorlog#pdbpm``)

- Remove versions from dependencies.

0.6
---

- Get rid of find-link point to http://dist.repoze.org in ``setup.py``.

- Bump ``ez_setup.py`` version.

0.5
---

- Depend on ``elementree`` 1.2.6 explicitly.

0.4
---

- Add ``ignore`` feature to configuration.  A value consisting of
  space-separated entry point names can be used here, indicating that
  these exception types should not be logged or kept in exception
  history.

- Allow ``__error_log__`` view path to be configured via ``path`` entry in
  Paste configuration.

- Place ``repoze.errorlog.path`` and ``repoze.errorlog.entryid`` in the
  WSGI environment to allow error-catching middleware and apps to
  compose URLs to errors.

0.3
---

- 0.2 didn't work as a filter. :-(

- Don't use ``zope.pagetemplate``, it has too many (potentially
  conflicting) dependencies.  Instead use ``meld`` for template views.

0.2
---

- Provide a TTW view (accessible via ``/__error_log__``) of recent
  tracebacks.

0.1
---

- Initial release.
