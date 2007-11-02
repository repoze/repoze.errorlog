import unittest
import logging

class TestTopLevelFuncs(unittest.TestCase):
    def test_make_errorlog_no_filename(self):
        from repoze.errorlog import make_errorlog
        elog = make_errorlog(None, None, channel='foo', keep=10)
        self.assertEqual(elog.channel, 'foo')
        self.assertEqual(elog.keep, 10)

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
        elog = self._makeOne(None, channel='foo', keep=10)
        self.assertEqual(elog.channel, 'foo')

    def test_log_no_exc(self):
        app = DummyApplication()
        elog = self._makeOne(app, channel='foo', keep=10)
        env = {}
        result = elog(env, None)
        self.assertEqual(app.environ, env)
        self.assertEqual(app.start_response, None)
        self.assertEqual(result, ['hello world'])
        
    def test_log_exc_no_channel(self):
        app = DummyApplication(KeyError)
        elog = self._makeOne(app, channel=None, keep=10)
        from StringIO import StringIO
        errors = StringIO()
        env = {'wsgi.errors':errors}
        self.assertRaises(KeyError, elog, env, None)
        self.failIf(errors.getvalue().find('KeyError') == -1)

    def test_log_exc_with_root_channel(self):
        app = DummyApplication(KeyError)
        root = ''
        elog = self._makeOne(app, channel=root, keep=10)
        self.assertRaises(KeyError, elog, {}, None)
        self.failIf(self.errorstream.getvalue().find('KeyError') == -1)

    def test_show_index_view(self):
        env = {'PATH_INFO':'/__error_log__', 'wsgi.url_scheme':'http',
               'SERVER_NAME':'localhost', 'SERVER_PORT':'8080'}
        elog = self._makeOne(None, channel=None, keep=10)
        L = []
        def start_response(code, headers):
            L.append((code, headers))
        from repoze.errorlog import Error
        elog.errors = [Error('1', 'description1', 'rendering1', 'time1', env),
                       Error('2', 'description2', 'rendering2', 'time2', env)]
        bodylist = elog(env, start_response)
        body = bodylist[0]
        self.failUnless('time1' in body)
        self.failUnless('time2' in body)
        self.failUnless('description1' in body)
        self.failUnless('description2' in body)
        self.failUnless('Recent Errors' in body)
        
    def test_show_entry_view_present(self):
        env = {'PATH_INFO':'/__error_log__', 'wsgi.url_scheme':'http',
               'SERVER_NAME':'localhost', 'SERVER_PORT':'8080',
               'QUERY_STRING':'entry=1'}
        elog = self._makeOne(None, channel=None, keep=10)
        L = []
        def start_response(code, headers):
            L.append((code, headers))
        from repoze.errorlog import Error
        elog.errors = [Error('1', 'description1', 'rendering1', 'time1', env)]
        bodylist = elog(env, start_response)
        body = bodylist[0]
        self.failUnless('rendering1' in body)
        self.failUnless('time1' in body)
        self.failUnless('Error ' in body)

    def test_show_entry_view_absent(self):
        env = {'PATH_INFO':'/__error_log__', 'wsgi.url_scheme':'http',
               'SERVER_NAME':'localhost', 'SERVER_PORT':'8080',
               'QUERY_STRING':'entry=1'}
        elog = self._makeOne(None, channel=None, keep=10)
        L = []
        def start_response(code, headers):
            L.append((code, headers))
        from repoze.errorlog import Error
        elog.errors = []
        bodylist = elog(env, start_response)
        body = bodylist[0]
        self.failUnless('Error Expired' in body)

    def test_insert_error(self):
        env = {'PATH_INFO':'/__error_log__', 'wsgi.url_scheme':'http',
               'SERVER_NAME':'localhost', 'SERVER_PORT':'8080',
               'QUERY_STRING':'entry=1'}
        elog = self._makeOne(None, channel=None, keep=10)
        import sys
        try:
            raise KeyError
        except:
            exc_info = sys.exc_info()
        elog.insert_error(exc_info, env)
        self.assertEqual(len(elog.errors), 1)

        # rollover
        elog.errors = [None] * 10
        elog.insert_error(exc_info, env)
        self.assertEqual(len(elog.errors), 10)
        from repoze.errorlog import Error
        self.assertEqual(elog.errors[0].__class__, Error)
        del exc_info

class DummyApplication:
    def __init__(self, exc=None):
        self.exc = exc

    def __call__(self, environ, start_response):
        if self.exc:
            raise self.exc
        self.environ = environ
        self.start_response = start_response
        return ['hello world']

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
