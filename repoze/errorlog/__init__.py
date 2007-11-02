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
import tempfile
import time
import StringIO

from paste.request import construct_url
from paste.request import parse_querystring

from zope.pagetemplate.pagetemplatefile import PageTemplateFile

_HERE = os.path.abspath(os.path.dirname(__file__))

class ErrorLog:
    def __init__(self, application, channel, keep):
        """ WSGI Middleware which logs errors to a confligurable place
        and exposes a web user interface to display the last N errors.

        o 'application' is the RHS in the WSGI "pipeline".

        o 'channel' is the logging "channel" (logger name) to send error log
          messages to.
        """
        self.application = application
        self.channel = channel
        self.keep = keep
        self.errors = []
        
    def __call__(self, environ, start_response):
        path_info = environ.get('PATH_INFO')

        if path_info == '/__error_log__':
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
            try:
                return self.application(environ, start_response)
            except:
                self.insert_error(sys.exc_info(), environ)
                if self.channel is None:
                    errors = environ.get('wsgi.errors')
                    if errors:
                        traceback.print_exc(None, errors)
                else:
                    logger = getLogger(self.channel)
                    logger.exception('')
                raise

    def index(self, url):
        template = PageTemplateFile(os.path.join(_HERE,'templates','errors.pt'))
        errors = self.errors
        return template(errors=self.errors)

    def entry(self, identifier):
        template = PageTemplateFile(os.path.join(_HERE,'templates','entry.pt'))
        error = self.get_error(identifier)
        # None is ok to pass as an error (the template handles this case)
        return template(error=error)

    def get_error(self, identifier):
        for error in self.errors:
            if error.identifier == identifier:
                return error

    def insert_error(self, exc_info, environ):
        if len(self.errors) >= self.keep:
            self.errors.pop()
        f = StringIO.StringIO()
        traceback.print_exception(exc_info[0], exc_info[1], exc_info[2], None,f)
        error = Error(str(time.time()), str(exc_info[0]), f.getvalue(),
                      time.ctime(), environ)
        self.errors.insert(0, error)
        
class Error:
    def __init__(self, identifier, description, tb_rendering, time, environ):
        self.identifier = identifier
        self.description = description
        self.text = tb_rendering + '\n\n' + pprint.pformat(environ)
        self.time = time
        url = '/__error_log__'
        self.url = url + '?entry=%s' % self.identifier
    
def make_errorlog(app, global_conf, **local_conf):
    channel = local_conf.get('channel', None)
    keep = int(local_conf.get('keep', 20))
    return ErrorLog(app, channel, keep)
