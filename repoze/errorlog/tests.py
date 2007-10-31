import unittest
import logging

class TestTopLevelFuncs(unittest.TestCase):
    def test_make_errorlog(self):
        from repoze.errorlog import make_errorlog
        elog = make_errorlog(None, None, channel='foo')
        self.assertEqual(elog.channel, 'foo')

class TestErrorLogging(unittest.TestCase):
    def setUp(self):
        from StringIO import StringIO
        self.errorstream = StringIO()
        logging.basicConfig(stream = self.errorstream)

    def tearDown(self):
        from logging import root
        root.handlers = []
        # grr
        from logging import _handlerList
        _handlerList[:] = []
        
    def _makeOne(self, *arg, **kw):
        from repoze.errorlog import ErrorLog
        return ErrorLog(*arg, **kw)

    def test_ctor(self):
        elog = self._makeOne(None, channel='foo')
        self.assertEqual(elog.channel, 'foo')

    def test_log_no_exc(self):
        app = DummyApplication()
        elog = self._makeOne(app, channel='foo')
        env = {}
        elog(env, None)
        self.assertEqual(app.environ, env)
        self.assertEqual(app.start_response, None)
        
    def test_log_exc_no_channel(self):
        app = DummyApplication(KeyError)
        elog = self._makeOne(app, channel=None)
        from StringIO import StringIO
        errors = StringIO()
        env = {'wsgi.errors':errors}
        self.assertRaises(KeyError, elog, env, None)
        self.failIf(errors.getvalue().find('KeyError') == -1)

    def test_log_exc_with_root_channel(self):
        app = DummyApplication(KeyError)
        root = ''
        elog = self._makeOne(app, channel=root)
        from StringIO import StringIO
        errors = StringIO()
        env = {'wsgi.errors':errors}
        self.assertRaises(KeyError, elog, env, None)
        self.failIf(self.errorstream.getvalue().find('KeyError') == -1)

class DummyApplication:
    def __init__(self, exc=None):
        self.exc = exc

    def __call__(self, environ, start_response):
        if self.exc:
            raise self.exc
        self.environ = environ
        self.start_response = start_response

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
