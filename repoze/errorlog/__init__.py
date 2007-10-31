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

import traceback
from logging import getLogger

class ErrorLog:
    def __init__(self, application, channel):
        """ WSGI Middlware which logs errors to a confligurable place
        and exposes a web user interface to display the last N errors.

        o 'application' is the RHS in the WSGI "pipeline".

        o 'channel' is the logging "channel" (logger name) to send error log
          messages to.
        """
        self.application = application
        self.channel = channel
        
    def __call__(self, environ, start_response):
        try:
            result = self.application(environ, start_response)
        except:
            if self.channel is None:
                errors = environ.get('wsgi.errors')
                if errors:
                    traceback.print_exc(None, errors)
            else:
                logger = getLogger(self.channel)
                logger.exception('')
            raise

def make_errorlog(app, global_conf, **local_conf):
    channel = local_conf.get('channel', None)
    return ErrorLog(app, channel)
