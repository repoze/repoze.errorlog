##############################################################################
#
# Copyright (c) 2007 Agendaless Consulting and Contributors.
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

from logging import getLogger
import os
import pprint
import sys
import traceback
import time
import StringIO

from paste.request import construct_url
from paste.request import parse_querystring

import meld3

_HERE = os.path.abspath(os.path.dirname(__file__))

class ErrorLog:
    def __init__(self, application, channel, keep, path, ignored_exceptions):
        """ WSGI Middleware which logs errors to a confligurable place
        and exposes a web user interface to display the last N errors.

        o 'application' is the RHS in the WSGI "pipeline".

        o 'channel' is the logging "channel" (logger name) to send error log
          messages to.

        o 'keep' is the number of errors to keep in exception history for
          through the web viewing.

        o path is the path to the error log view (e.g. '/__error_log__').

        o ignored_exceptions is a list of exceptions (Python references) to
          ignore (to refrain from logging or adding to exception history).
        """
        self.application = application
        self.channel = channel
        self.keep = keep
        self.path = path
        self.counter = 0
        self.ignored_exceptions = ignored_exceptions
        self.errors = []

    def new_identifier(self):
        identifier = str(self.counter)
        self.counter += 1
        return identifier
        
    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO')

        if path_info == self.path:
            # we're being asked to render a view
            querydata = dict(parse_querystring(environ))
            if 'entry' in querydata:
                body = self.entry(querydata['entry'])
            else:
                url = construct_url(environ, with_query_string=False)
                body = self.index(url)
            start_response('200 OK', [('content-type', 'text/html'),
                                      ('content-length', str(len(body)))])
            return [body]
        else:
            # we need to try to catch an error
            identifier = self.new_identifier()
            # we place the error log path and identifier in the
            # environment so the application or other middleware can
            # form a URL to the exception
            environ['repoze.errorlog.path'] = self.path
            environ['repoze.errorlog.entryid'] = identifier
            try:
                return self.application(environ, start_response)
            except self.ignored_exceptions:
                # just reraise an ignored exception
                raise
            except:
                self.insert_error(identifier, sys.exc_info(), environ)
                if self.channel is None:
                    errors = environ.get('wsgi.errors')
                    if errors:
                        traceback.print_exc(None, errors)
                else:
                    logger = getLogger(self.channel)
                    logger.exception('')
                raise

    def index(self, url):
        template = os.path.join(_HERE, 'templates', 'errors.html')
        root = meld3.parse_xml(template)
        if self.errors:
            iterator = root.findmeld('error_li').repeat(self.errors)
            for li_element, error in iterator:
                t = li_element.findmeld('error_time')
                t.content(error.time)
                url = li_element.findmeld('error_url')
                url.attributes(href=error.url)
                url.content(error.description)
        else:
            content = root.findmeld('content')
            content.content('<h1>No Recent Errors</h1>', structure=True)
        return root.write_xhtmlstring()

    def entry(self, identifier):
        template = os.path.join(_HERE, 'templates', 'entry.html')
        error = self.get_error(identifier)
        root = meld3.parse_xml(template)
        if error:
            header = root.findmeld('header')
            header.content('Error at %s' % error.time)
            text = root.findmeld('text')
            text.content(error.text)
        else:
            header = root.findmeld('header')
            header.content('Error Expired')
            text_area = root.findmeld('text_area')
            text_area.content(
                "<p>The error you're attempting to view has been flushed from "
                "the online error log history.</p>", structure=True)
        return root.write_xhtmlstring()

    def get_error(self, identifier):
        for error in self.errors:
            if error.identifier == identifier:
                return error

    def insert_error(self, identifier, exc_info, environ):
        if len(self.errors) >= self.keep:
            self.errors.pop()
        f = StringIO.StringIO()
        # we can't unpack the exception tuple or we'd cause a cycle
        traceback.print_exception(exc_info[0],exc_info[1],exc_info[2],None,f)
        desc = str(exc_info[0])
        tb_rendering = f.getvalue()
        time_str = time.ctime()
        url = self.path +'?entry=%s' % identifier
        error = Error(identifier, desc, tb_rendering, time_str, environ, url)
        self.errors.insert(0, error)
        
class Error:
    def __init__(self, identifier, desc, tb_rendering, time, environ, url):
        self.identifier = identifier
        self.description = desc
        self.text = tb_rendering + '\n\n' + pprint.pformat(environ)
        self.time = time
        self.url = url
    
def make_errorlog(app, global_conf, **local_conf):
    channel = local_conf.get('channel', None)
    keep = int(local_conf.get('keep', 20))
    path = local_conf.get('path', '/__error_log__')
    ignore = local_conf.get('ignore', None)
    # e.g. Paste.httpexceptions.HTTPFound,
    # Paste.httpexceptions.HTTPUnauthorized, Paste.httpexceptions.HTTPNotFound
    ignored_exceptions = []
    if ignore:
        from pkg_resources import EntryPoint
        ignore_names = [ name.strip() for name in ignore.split() ]
        for name in ignore_names:
            if __builtins__.has_key(name):
                ignored_exc = __builtins__[name]
            else:
                ignored_exc = EntryPoint.parse('x=%s' % name).load(False)
            ignored_exceptions.append(ignored_exc)
    ignored_exceptions = tuple(ignored_exceptions)
    return ErrorLog(app, channel, keep, path, ignored_exceptions)

