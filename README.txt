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
    configuration option at this time is "channel".  To configure
    repoze.errorlog to use the 'Repoze' logging channel, which sends
    to the 'Repoze' logging channel, as if you had send to a logger
    from code where you did 'from logging import getLogger;
    logger = getLogger("Repoze")'::

      [filter:errorlog]
      channel = Repoze

    By default, no channel is configured, and tracebacks are sent to
    the 'wsgi.errors' file handle (which should cause the errors to
    show up in your server's error log).

    To use the reconfigured filter in the
    pipeline::

      [pipeline:main]
      pipeline = egg:Paste#cgitb
                 errorlog
                 myapp

