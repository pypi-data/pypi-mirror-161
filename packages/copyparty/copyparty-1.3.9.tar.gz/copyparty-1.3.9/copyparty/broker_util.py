# coding: utf-8
from __future__ import print_function, unicode_literals

import argparse
import traceback

from queue import Queue

from .__init__ import TYPE_CHECKING
from .authsrv import AuthSrv
from .util import Pebkac

try:
    raise Exception()

    from .util import RootLogger
except:
    pass

if TYPE_CHECKING:
    from .httpsrv import HttpSrv


class ExceptionalQueue(Queue, object):
    def get(self, block  = True, timeout  = None)  :
        rv = super(ExceptionalQueue, self).get(block, timeout)

        if isinstance(rv, list):
            if rv[0] == "exception":
                if rv[1] == "pebkac":
                    raise Pebkac(*rv[2:])
                else:
                    raise Exception(rv[2])

        return rv


class BrokerCli(object):
    """
    helps mypy understand httpsrv.broker but still fails a few levels deeper,
    for example resolving httpconn.* in httpcli -- see lines tagged #mypy404
    """

    def __init__(self)  :
        self.log  = None
        self.args  = None
        self.asrv  = None
        self.httpsrv  = None

    def ask(self, dest , *args )  :
        return ExceptionalQueue(1)

    def say(self, dest , *args )  :
        pass


def try_exec(want_retval  , func , *args )  :
    try:
        return func(*args)

    except Pebkac as ex:
        if not want_retval:
            raise

        return ["exception", "pebkac", ex.code, str(ex)]

    except:
        if not want_retval:
            raise

        return ["exception", "stack", traceback.format_exc()]
