repoze.errorlog README

  Overview

    This package implements a WSGI Middleware filter which intercepts
    exceptions and writes them to a Python 'logging' module channel
    (or the 'wsgi.errors' filehandle, if no channel is configured).

  Installation

    The simple way::

      $ bin/easy_install --find-links=http://dist.repoze.org/ repoze.errorlog

  Configuration
    
    If you want to use the default configuration, you can just include the
    filter in your application's pipeline.  

        [pipeline:main]
        pipeline = egg:Paste#cgitb
                   egg:repoze.errorlog#errorlog
                   zope2

    If you want to override the default configuration, you need to
    make a separate section for the filter.  The only Paste
    configuration options at this time are "channel" and "keep".  To
    configure repoze.errorlog to use the 'Repoze' logging channel,
    which sends to the 'Repoze' logging channel, as if you had send to
    a logger from code where you did 'from logging import getLogger;
    logger = getLogger("Repoze")' and to keep 50 tracebacks around for
    through-the-web exception viewing, configure like so::

      [filter:errorlog]
      channel = Repoze
      keep = 50

    By default, no channel is configured, and tracebacks are sent to
    the 'wsgi.errors' file handle (which should cause the errors to
    show up in your server's error log).  By default, the exception
    history length ('keep') is 20.

    To use the reconfigured filter in the
    pipeline::

      [pipeline:main]
      pipeline = egg:Paste#cgitb
                 errorlog
                 myapp

  Usage

    To view recent tracebacks via your browser (exception history),
    visit the '/__error_log__' path at the hostname represented by
    your server.  A view will be presented showing you all recent
    tracebacks.  Clicking on one will bring you to a page which shows
    you the traceback and a rendering of the WSGI environment which
    was present at the time the exception occurred.

