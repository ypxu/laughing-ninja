# Gunicorn config file

import  multiprocessing

workers = multiprocessing.cpu_count() * 2 + 1
bind = ['unix:/tmp/gunicorn.%d.sock' % i for i in xrange(workers)]
daemon = False
debug = True
loglevel= 'debug'
logfile = '-'
accesslog = '-'
