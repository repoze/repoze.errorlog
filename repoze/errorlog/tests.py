import sys
import unittest
import logging

class TestTopLevelFuncs(unittest.TestCase):
    def test_make_errorlog_no_filename(self):
        from repoze.errorlog import make_errorlog
        me = sys.modules[__name__].__name__
        dummy = '%s:DummyException' % me
        elog = make_errorlog(None, None, channel='foo', keep=10,
                             path='/__error_log__',
                             ignore='KeyError AttributeError %s' % dummy)
        self.assertEqual(elog.channel, 'foo')
        self.assertEqual(elog.keep, 10)
        self.assertEqual(elog.path, '/__error_log__')
        self.assertEqual(elog.counter, 0)
        self.assertEqual(elog.errors, [])
        self.assertEqual(elog.ignored_exceptions, (KeyError, AttributeError,
                                                   DummyException))

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
        elog = self._makeOne(None, channel='foo', keep=10,
                             path='/__error_log__', ignored_exceptions=())
        self.assertEqual(elog.channel, 'foo')

    def test_log_no_exc(self):
        app = DummyApplication()
        elog = self._makeOne(app, channel='foo', keep=10,
                             path='/__error_log__', ignored_exceptions=())
        env = {}
        result = elog(env, None)
        self.assertEqual(app.environ, env)
        self.assertEqual(app.start_response, None)
        self.assertEqual(result, ['hello world'])
        self.assertEqual(env['repoze.errorlog.path'], '/__error_log__')
        self.assertEqual(env['repoze.errorlog.entryid'], '0')
        
    def test_log_exc_no_channel(self):
        app = DummyApplication(KeyError)
        elog = self._makeOne(app, channel=None, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        from StringIO import StringIO
        errors = StringIO()
        env = {'wsgi.errors':errors}
        self.assertRaises(KeyError, elog, env, None)
        self.failUnless('KeyError' in errors.getvalue())
        self.assertEqual(env['repoze.errorlog.path'], '/__error_log__')
        self.assertEqual(env['repoze.errorlog.entryid'], '0')

    def test_log_exc_with_root_channel(self):
        app = DummyApplication(KeyError)
        root = ''
        elog = self._makeOne(app, channel=root, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        env = {}
        self.assertRaises(KeyError, elog, env, None)
        self.failUnless('KeyError' in self.errorstream.getvalue())
        self.assertEqual(env['repoze.errorlog.path'], '/__error_log__')
        self.assertEqual(env['repoze.errorlog.entryid'], '0')

    def test_log_ignored_builtin_exceptions(self):
        app = DummyApplication(KeyError)
        from StringIO import StringIO
        errors = StringIO()
        env = {'wsgi.errors':errors}
        elog = self._makeOne(app, channel=None, keep=10,
                             path='/__error_log__',
                             ignored_exceptions=(KeyError, AttributeError))
        self.assertRaises(KeyError, elog, env, None)
        self.assertEqual(errors.getvalue(), '')
        self.assertEqual(elog.errors, [])

    def test_identifier_counter(self):
        app = DummyApplication(KeyError)
        elog = self._makeOne(app, channel=None, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        from StringIO import StringIO
        errors = StringIO()
        env = {'wsgi.errors':errors}
        self.assertRaises(KeyError, elog, env, None)
        self.assertRaises(KeyError, elog, env, None)
        self.assertRaises(KeyError, elog, env, None)
        self.assertEqual(env['repoze.errorlog.path'], '/__error_log__')
        self.assertEqual(env['repoze.errorlog.entryid'], '2')

    def test_show_index_view(self):
        env = {'PATH_INFO':'/__error_log__', 'wsgi.url_scheme':'http',
               'SERVER_NAME':'localhost', 'SERVER_PORT':'8080'}
        elog = self._makeOne(None, channel=None, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        L = []
        def start_response(code, headers):
            L.append((code, headers))
        from repoze.errorlog import Error
        elog.errors = [
            Error('1','description1','rendering1','time1',env,'url1'),
            Error('2','description2','rendering2','time2',env,'url2')
            ]
        bodylist = elog(env, start_response)
        body = bodylist[0]
        self.failUnless('time1' in body)
        self.failUnless('time2' in body)
        self.failUnless('description1' in body)
        self.failUnless('description2' in body)
        self.failUnless('Recent Errors' in body)

    def test_show_index_view_noerrors(self):
        env = {'PATH_INFO':'/__error_log__', 'wsgi.url_scheme':'http',
               'SERVER_NAME':'localhost', 'SERVER_PORT':'8080'}
        elog = self._makeOne(None, channel=None, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        L = []
        def start_response(code, headers):
            L.append((code, headers))
        elog.errors = []
        bodylist = elog(env, start_response)
        body = bodylist[0]
        self.failUnless('No Recent Errors' in body)
        
    def test_show_entry_view_present(self):
        env = {'PATH_INFO':'/__error_log__', 'wsgi.url_scheme':'http',
               'SERVER_NAME':'localhost', 'SERVER_PORT':'8080',
               'QUERY_STRING':'entry=1'}
        elog = self._makeOne(None, channel=None, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        L = []
        def start_response(code, headers):
            L.append((code, headers))
        from repoze.errorlog import Error
        elog.errors = [
            Error('1','description1','rendering1','time1',env,'url1'),
            ]
        bodylist = elog(env, start_response)
        body = bodylist[0]
        self.failUnless('rendering1' in body)
        self.failUnless('time1' in body)
        self.failUnless('Error ' in body)

    def test_show_entry_view_absent(self):
        env = {'PATH_INFO':'/__error_log__', 'wsgi.url_scheme':'http',
               'SERVER_NAME':'localhost', 'SERVER_PORT':'8080',
               'QUERY_STRING':'entry=1'}
        elog = self._makeOne(None, channel=None, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        L = []
        def start_response(code, headers):
            L.append((code, headers))
        elog.errors = []
        bodylist = elog(env, start_response)
        body = bodylist[0]
        self.failUnless('Error Expired' in body)

    def test_insert_error(self):
        env = {'PATH_INFO':'/__error_log__', 'wsgi.url_scheme':'http',
               'SERVER_NAME':'localhost', 'SERVER_PORT':'8080',
               'QUERY_STRING':'entry=1'}
        elog = self._makeOne(None, channel=None, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        import sys
        try:
            raise KeyError
        except:
            exc_info = sys.exc_info()
        elog.insert_error('id', exc_info, env)
        self.assertEqual(len(elog.errors), 1)

        # rollover
        elog.errors = [None] * 10
        elog.insert_error('id2', exc_info, env)
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

class DummyException(Exception):
    pass

