# coding: utf-8
from __future__ import print_function, unicode_literals

import tempfile
from datetime import datetime

from .bos import bos

try:
    raise Exception()

    from .util import NamedLogger
except:
    pass


class StreamArc(object):
    def __init__(
        self,
        log ,
        fgen    ,
        **kwargs 
    ):
        self.log = log
        self.fgen = fgen

    def gen(self)    :
        pass


def errdesc(errors  )    :
    report = ["copyparty failed to add the following files to the archive:", ""]

    for fn, err in errors:
        report.extend([" file: {}".format(fn), "error: {}".format(err), ""])

    with tempfile.NamedTemporaryFile(prefix="copyparty-", delete=False) as tf:
        tf_path = tf.name
        tf.write("\r\n".join(report).encode("utf-8", "replace"))

    dt = datetime.utcnow().strftime("%Y-%m%d-%H%M%S")

    bos.chmod(tf_path, 0o444)
    return {
        "vp": "archive-errors-{}.txt".format(dt),
        "ap": tf_path,
        "st": bos.stat(tf_path),
    }, report
