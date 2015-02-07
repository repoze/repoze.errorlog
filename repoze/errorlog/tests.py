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
        from ._compat import NativeStream
        self.errorstream = NativeStream()
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
        from ._compat import NativeStream
        errors = NativeStream()
        app = DummyApplication(KeyError)
        elog = self._makeOne(app, channel=None, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        env = {'wsgi.errors':errors}
        self.assertRaises(KeyError, elog, env, None)
        self.assertTrue('KeyError' in errors.getvalue())
        self.assertEqual(env['repoze.errorlog.path'], '/__error_log__')
        self.assertEqual(env['repoze.errorlog.entryid'], '0')

    def test_log_exc_with_root_channel(self):
        app = DummyApplication(KeyError)
        root = ''
        elog = self._makeOne(app, channel=root, keep=10,
                             path='/__error_log__', ignored_exceptions=())
        env = {}
        self.assertRaises(KeyError, elog, env, None)
        self.assertTrue('KeyError' in self.errorstream.getvalue())
        self.assertEqual(env['repoze.errorlog.path'], '/__error_log__')
        self.assertEqual(env['repoze.errorlog.entryid'], '0')

    def test_log_ignored_builtin_exceptions(self):
        from ._compat import NativeStream
        errors = NativeStream()
        app = DummyApplication(KeyError)
        env = {'wsgi.errors':errors}
        elog = self._makeOne(app, channel=None, keep=10,
                             path='/__error_log__',
                             ignored_exceptions=(KeyError, AttributeError))
        self.assertRaises(KeyError, elog, env, None)
        self.assertEqual(errors.getvalue(), '')
        self.assertEqual(elog.errors, [])

    def test_identifier_counter(self):
        from ._compat import NativeStream
        errors = NativeStream()
        app = DummyApplication(KeyError)
        elog = self._makeOne(app, channel=None, keep=10,
                             path='/__error_log__', ignored_exceptions=())
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
        self.assertTrue(b'time1' in body)
        self.assertTrue(b'time2' in body)
        self.assertTrue(b'description1' in body)
        self.assertTrue(b'description2' in body)
        self.assertTrue(b'Recent Errors' in body)

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
        self.assertTrue(b'No Recent Errors' in body)
        
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
        self.assertTrue(b'rendering1' in body)
        self.assertTrue(b'time1' in body)
        self.assertTrue(b'Error ' in body)

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
        self.assertTrue(b'Error Expired' in body)

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


class Test__parse_querystring(unittest.TestCase):

    def _callFUT(self, environ):
        from repoze.errorlog import _parse_querystring
        return _parse_querystring(environ)

    def test_no_qs(self):
        environ = {}
        found = self._callFUT(environ)
        self.assertEqual(found, [])

    def test_simple(self):
        environ = {'QUERY_STRING': 'a=1&b=2&c=3'}
        found = self._callFUT(environ)
        self.assertEqual(found,
                         [('a', '1'), ('b', '2'), ('c', '3')])

    def test_w_repeats(self):
        environ = {'QUERY_STRING': 'a=1&b=2&c=3&b=4'}
        found = self._callFUT(environ)
        self.assertEqual(found,
                         [('a', '1'), ('b', '2'), ('c', '3'), ('b', '4')])

    def test_w_empty(self):
        environ = {'QUERY_STRING': 'a&b&c=&d=1'}
        found = self._callFUT(environ)
        self.assertEqual(found, [('a', ''), ('b', ''), ('c', ''), ('d', '1')])


class Test__construct_url(unittest.TestCase):

    def _callFUT(self, environ):
        from repoze.errorlog import _construct_url
        return _construct_url(environ)

    def test_w_HTTP_HOST_wo_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com'})
        self.assertEqual(self._callFUT(environ), 'http://example.com')

    def test_w_HTTP_HOST_w_default_http_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com:80'})
        self.assertEqual(self._callFUT(environ), 'http://example.com')

    def test_w_HTTP_HOST_w_non_default_http_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com:8080'})
        self.assertEqual(self._callFUT(environ), 'http://example.com:8080')

    def test_w_HTTP_HOST_w_default_https_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com:443',
                                'wsgi.url_scheme': 'https',
                               })
        self.assertEqual(self._callFUT(environ), 'https://example.com')

    def test_w_HTTP_HOST_w_non_default_https_port(self):
        environ = _makeEnviron({'HTTP_HOST': 'example.com:4443',
                                'wsgi.url_scheme': 'https',
                               })
        self.assertEqual(self._callFUT(environ), 'https://example.com:4443')

    def test_wo_HTTP_HOST_w_default_http_port(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '80',
                               })
        self.assertEqual(self._callFUT(environ), 'http://example.com')

    def test_wo_HTTP_HOST_w_non_default_http_port(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '8080',
                               })
        self.assertEqual(self._callFUT(environ), 'http://example.com:8080')

    def test_wo_HTTP_HOST_w_default_https_port(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '443',
                                'wsgi.url_scheme': 'https',
                               })
        self.assertEqual(self._callFUT(environ), 'https://example.com')

    def test_wo_HTTP_HOST_w_non_default_https_port(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '4443',
                                'wsgi.url_scheme': 'https',
                               })
        self.assertEqual(self._callFUT(environ), 'https://example.com:4443')

    def test_w_SCRIPT_NAME(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '80',
                                'SCRIPT_NAME': '/script/name',
                               })
        self.assertEqual(self._callFUT(environ),
                         'http://example.com/script/name')

    def test_w_PATH_INFO(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '80',
                                'PATH_INFO': '/path/info',
                               })
        self.assertEqual(self._callFUT(environ),
                         'http://example.com/path/info')

    def test_w_SCRIPT_NAME_and_PATH_INFO(self):
        environ = _makeEnviron({'SERVER_NAME': 'example.com',
                                'SERVER_PORT': '80',
                                'SCRIPT_NAME': '/script/name',
                                'PATH_INFO': '/path/info',
                               })
        self.assertEqual(self._callFUT(environ),
                         'http://example.com/script/name/path/info')


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


def _makeEnviron(override=None):
    from ._compat import NativeStream
    environ = {
        'SERVER_NAME': 'localhost',
        'SERVER_PORT': '80',
        'wsgi.version': (1, 0),
        'wsgi.multiprocess': False,
        'wsgi.multithread': True,
        'wsgi.run_once': False,
        'wsgi.url_scheme': 'http',
        'wsgi.input': NativeStream('hello world'),
        }
    if override is not None:
        environ.update(override)
    return environ
