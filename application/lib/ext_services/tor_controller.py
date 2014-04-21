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
from mamba.utils import config
from twisted.internet import reactor


class TorController(object):
    """Controller class for starting up and shutting down instances of tor
    """

    def __init__(self):
        super(TorController, self).__init__()
        self.on_finish = None

    def spawn(self, on_finish=None):
        """ Spawns a new isntance of tor process """

        tor_config = txtorcon.TorConfig()
        tor_config.SOCKSPort = config.Application().tor_socks_port
        tor_config.ControlPort = config.Application().tor_control_port

        d = txtorcon.launch_tor(
            tor_config, reactor, progress_updates=self.updates, timeout=60)

        d.addCallback(functools.partial(self.setup_complete, tor_config))
        d.addErrback(self.setup_failed)

        if on_finish is not None:
            self.on_finish = on_finish

    def updates(self, prog, tag, summary):
        """ Logs the current progress of the startup process """

        log.msg("{}%: {}".format(prog, summary))

    def setup_complete(self, tor_config, proto):
        """ Called when the setup has been completed sucdcessfully """

        log.msg("setup complete:", proto)
        self.on_finish()

    def setup_failed(self, arg):
        """ Called if a failure occurs """

        log.msg("SETUP FAILED", arg)
