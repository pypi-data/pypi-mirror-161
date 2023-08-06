# coding: utf-8
from __future__ import print_function, unicode_literals

import argparse  # typechk
import os
import re
import socket
import threading  # typechk
import time

try:
    HAVE_SSL = True
    import ssl
except:
    HAVE_SSL = False

from . import util as Util
from .__init__ import TYPE_CHECKING, E
from .authsrv import AuthSrv  # typechk
from .httpcli import HttpCli
from .ico import Ico
from .mtag import HAVE_FFMPEG
from .th_cli import ThumbCli
from .th_srv import HAVE_PIL, HAVE_VIPS
from .u2idx import U2idx

try:
    raise Exception()
except:
    pass

if TYPE_CHECKING:
    from .httpsrv import HttpSrv


class HttpConn(object):
    """
    spawned by HttpSrv to handle an incoming client connection,
    creates an HttpCli for each request (Connection: Keep-Alive)
    """

    def __init__(
        self, sck , addr  , hsrv 
    )  :
        self.s = sck
        self.sr  = None
        self.addr = addr
        self.hsrv = hsrv

        self.mutex  = hsrv.mutex  # mypy404
        self.args  = hsrv.args  # mypy404
        self.asrv  = hsrv.asrv  # mypy404
        self.cert_path = hsrv.cert_path
        self.u2fh  = hsrv.u2fh  # mypy404

        enth = (HAVE_PIL or HAVE_VIPS or HAVE_FFMPEG) and not self.args.no_thumb
        self.thumbcli  = ThumbCli(hsrv) if enth else None  # mypy404
        self.ico  = Ico(self.args)  # mypy404

        self.t0  = time.time()  # mypy404
        self.stopping = False
        self.nreq  = 0  # mypy404
        self.nbyte  = 0  # mypy404
        self.u2idx  = None
        self.log_func  = hsrv.log  # mypy404
        self.log_src  = "httpconn"  # mypy404
        self.lf_url  = (
            re.compile(self.args.lf_url) if self.args.lf_url else None
        )  # mypy404
        self.set_rproxy()

    def shutdown(self)  :
        self.stopping = True
        try:
            self.s.shutdown(socket.SHUT_RDWR)
            self.s.close()
        except:
            pass

    def set_rproxy(self, ip  = None)  :
        if ip is None:
            color = 36
            ip = self.addr[0]
            self.rproxy = None
        else:
            color = 34
            self.rproxy = ip

        self.ip = ip
        self.log_src = "{} \033[{}m{}".format(ip, color, self.addr[1]).ljust(26)
        return self.log_src

    def respath(self, res_name )  :
        return os.path.join(E.mod, "web", res_name)

    def log(self, msg , c   = 0)  :
        self.log_func(self.log_src, msg, c)

    def get_u2idx(self)  :
        # one u2idx per tcp connection;
        # sqlite3 fully parallelizes under python threads
        if not self.u2idx:
            self.u2idx = U2idx(self)

        return self.u2idx

    def _detect_https(self)  :
        method = None
        if self.cert_path:
            try:
                method = self.s.recv(4, socket.MSG_PEEK)
            except socket.timeout:
                return False
            except AttributeError:
                # jython does not support msg_peek; forget about https
                method = self.s.recv(4)
                self.sr = Util.Unrecv(self.s, self.log)
                self.sr.buf = method

                # jython used to do this, they stopped since it's broken
                # but reimplementing sendall is out of scope for now
                if not getattr(self.s, "sendall", None):
                    self.s.sendall = self.s.send  # type: ignore

            if len(method) != 4:
                err = "need at least 4 bytes in the first packet; got {}".format(
                    len(method)
                )
                if method:
                    self.log(err)

                self.s.send(b"HTTP/1.1 400 Bad Request\r\n\r\n" + err.encode("utf-8"))
                return False

        return method not in [None, b"GET ", b"HEAD", b"POST", b"PUT ", b"OPTI"]

    def run(self)  :
        self.sr = None
        if self.args.https_only:
            is_https = True
        elif self.args.http_only or not HAVE_SSL:
            is_https = False
        else:
            # raise Exception("asdf")
            is_https = self._detect_https()

        if is_https:
            if self.sr:
                self.log("TODO: cannot do https in jython", c="1;31")
                return

            self.log_src = self.log_src.replace("[36m", "[35m")
            try:
                ctx = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
                ctx.load_cert_chain(self.cert_path)
                if self.args.ssl_ver:
                    ctx.options &= ~self.args.ssl_flags_en
                    ctx.options |= self.args.ssl_flags_de
                    # print(repr(ctx.options))

                if self.args.ssl_log:
                    try:
                        ctx.keylog_filename = self.args.ssl_log
                    except:
                        self.log("keylog failed; openssl or python too old")

                if self.args.ciphers:
                    ctx.set_ciphers(self.args.ciphers)

                self.s = ctx.wrap_socket(self.s, server_side=True)
                msg = [
                    "\033[1;3{:d}m{}".format(c, s)
                    for c, s in zip([0, 5, 0], self.s.cipher())  # type: ignore
                ]
                self.log(" ".join(msg) + "\033[0m")

                if self.args.ssl_dbg and hasattr(self.s, "shared_ciphers"):
                    ciphers = self.s.shared_ciphers()
                    assert ciphers
                    overlap = [str(y[::-1]) for y in ciphers]
                    self.log("TLS cipher overlap:" + "\n".join(overlap))
                    for k, v in [
                        ["compression", self.s.compression()],
                        ["ALPN proto", self.s.selected_alpn_protocol()],
                        ["NPN proto", self.s.selected_npn_protocol()],
                    ]:
                        self.log("TLS {}: {}".format(k, v or "nah"))

            except Exception as ex:
                em = str(ex)

                if "ALERT_BAD_CERTIFICATE" in em:
                    # firefox-linux if there is no exception yet
                    self.log("client rejected our certificate (nice)")

                elif "ALERT_CERTIFICATE_UNKNOWN" in em:
                    # android-chrome keeps doing this
                    pass

                else:
                    self.log("handshake\033[0m " + em, c=5)

                return

        if not self.sr:
            self.sr = Util.Unrecv(self.s, self.log)

        while not self.stopping:
            self.nreq += 1
            cli = HttpCli(self)
            if not cli.run():
                return
