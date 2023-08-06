"""Aries agent for python wsgi application server
Jennifer version 5 agent for python
"""

import os
from . import config
from . import wrap

if os.getenv('PY_DBG'):
    from .network_logger import LogSocket

# https://pypi.org/project/jennifer-python/
# pip install jennifer-python
__version__ = '5.6.0.15'
__author__ = 'JENNIFER'

log_socket = None


def get_log_socket():
    global log_socket

    if os.getenv('PY_DBG'):
        if log_socket is None:
            log_socket = LogSocket(39999)

    return log_socket


# Not used
# def wsgi_app(app):
#     if os.environ.get('JENNIFER_MASTER_ADDRESS') is not None:
#         return wrap.wrap_wsgi_app(app)
#     return app
