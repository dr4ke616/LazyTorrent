# -*- coding: utf-8 -*-
"""
.. module:: TransmissionController
    :synopsis: Small wrapper for sending requests to website using Twisted
        over the tor network (optionally)

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import os
import glob
import signal

from mamba.utils import config
from twisted.python import log, filepath
from twisted.internet import reactor, protocol


class TransmissionNotFound(RuntimeError):
    """
    Raised in case the transmissoin binary was unspecified and could
    not be found.
    """


class TransmissionProtocol(protocol.ProcessProtocol):
    """ ProcessProtocol subclass for starting up and
        shutting down instances of transmissoin
    """

    def __init__(self):
        self.data = ''

    def connectionMade(self):
        """ The output recieved callback """

        log.msg('Connection made to transmissoin process')

    def outReceived(self, data):
        """ The output recieved callback """

        log.msg('Transmissoin Process recieved {} bytes'.format(len(data)))
        self.data = self.data + data

    def errReceived(self, data):
        """ The error recieved callback """

        raise RuntimeError('Transmissoin error, data {}'.format(data))

    def processEnded(self, status):
        """ The process ended callback """

        if status.value.exitCode != 0:
            raise RuntimeError(
                'Transmissoin Process quit unexpectedly, status {}'
                .format(status.value.exitCode)
            )

        log.msg(
            'Transmissoin daemon started, status {}'
            .format(status.value.exitCode)
        )


class TransmissionController(object):
    """docstring for TransmissionController"""

    def __init__(self):
        super(TransmissionController, self).__init__()

    def spawn(self):
        """ Spawns a new instance of Transmissoin """

        use_daemon = config.Application().transmission_client['use_daemon']
        if not use_daemon:
            log.msg('Not using Transmission daemon.')
            return

        binary = self.find_binary()
        tp = TransmissionProtocol()

        reactor.addSystemEventTrigger('before', 'shutdown', self.on_exit)
        try:
            transport = reactor.spawnProcess(
                tp, binary, args=['transmission-daemon'],
                env={'HOME': os.environ['HOME']}
            )
            transport.closeStdin()
        except RuntimeError, e:
            raise e

    def find_binary(self, globs=(
                    '/usr/sbin/', '/usr/bin/',
                    '/Applications/Transmissoin_*.app/Contents/MacOS/')):

        for pattern in globs:
            for path in glob.glob(pattern):
                transmissionbin = os.path.join(path, 'transmission-daemon')
                if self._is_executable(transmissionbin):
                    return transmissionbin

        raise TransmissionNotFound('No Transmissoin binary found')

    def on_exit(self):
        """ Just before application shuts down kill Transmissoin """

        transmission_pid = filepath.FilePath('transmission.pid')
        if not transmission_pid.exists():
            log.err('error: transmission.pid file can\'t be found.')
            raise

        pid = transmission_pid.open().read()
        log.msg(
            'Killing Transmission daemon: process id {} with SIGINT signal'
            .format(pid)
        )

        try:
            filepath.os.kill(int(pid), signal.SIGINT)
        except:
            raise

        log.msg('Killed Transmission daemon {}...'.format(pid))

    def _is_executable(self, path):
        """Checks if the given path points to an existing, executable file"""

        return os.path.isfile(path) and os.access(path, os.X_OK)
