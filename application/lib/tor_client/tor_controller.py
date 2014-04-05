# -*- coding: utf-8 -*-
"""
.. module:: TorController
    :synopsis: Small wrapper for sending requests to website using Twisted
        over the tor network (optionally)

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import txtorcon
import functools

from twisted.python import log
from twisted.internet import reactor
from mamba.utils import config


class TorController(object):
    """Controller class for starting up and shutting down instances of tor
    """

    def __init__(self):
        super(TorController, self).__init__()
        self.initialzed = False

    def spawn(self):
        if not self.initialzed:
            tor_config = txtorcon.TorConfig()
            tor_config.SOCKSPort = config.Application().tor_socks_port
            tor_config.ControlPort = config.Application().tor_control_port

            d = txtorcon.launch_tor(
                tor_config, reactor, progress_updates=self.updates, timeout=60)

            d.addCallback(functools.partial(self.setup_complete, tor_config))
            d.addErrback(self.setup_failed)

    def updates(self, prog, tag, summary):
        log.msg("{}%: {}".format(prog, summary))

    def setup_complete(self, tor_config, proto):
        log.msg("setup complete:", proto)
        self.initialzed = True

    def setup_failed(self, arg):
        log.msg("SETUP FAILED", arg)
