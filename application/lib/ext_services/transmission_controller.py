# -*- coding: utf-8 -*-
"""
.. module:: TransmissionController
    :synopsis: Small wrapper for sending requests to website using Twisted
        over the tor network (optionally)

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import sys
import time
import signal
import subprocess

from mamba.utils import config
from twisted.python import log, filepath


class TransmissionController(object):
    """Controller class for starting up and shutting down instances of tor
    """

    def __init__(self):
        super(TransmissionController, self).__init__()

    def spawn(self):
        use_daemon = config.Application().transmission_client['use_daemon']
        self.kill_daemons()

        if use_daemon:
            self.start()

    def start(self):
        """ Starts the transmission daemon """

        if filepath.exists('transmission.pid'):
            log.err(
                'error: transmission.pid found, seems like the application is '
                'running already. If the application is not running, please '
                'delete transmission.pid and try again'
            )
            sys.exit(-1)

        p = subprocess.Popen(['transmission-daemon'])
        output, error = p.communicate()
        log.err('Starting transmission daemon')

        if error is not None and error is not '':
            raise RuntimeError(error)

        log.err('Transmission daemon started...')
        time.sleep(0.5)

    def handle_stop(self):
        """ Kills the transmission daemon """

        transmission_pid = filepath.FilePath('transmission.pid')
        if not transmission_pid.exists():
            log.err('error: transmission.pid file can\'t be found.')
            sys.exit(-1)

        pid = transmission_pid.open().read()
        log.err('Killing process id {} with SIGINT signal'.format(pid))
        try:
            filepath.os.kill(int(pid), signal.SIGINT)
        except:
            raise

        log.err('Killed Transmission daemon {}...'.format(pid))
        time.sleep(0.5)

    def kill_daemons(self):
        """ Kills any transmission daemons that might be still running
            Run as sudo in order to kill system daemon
        """

        def run_psx():
            p = subprocess.Popen(
                "ps aux | grep [t]ransmission-daemon "
                "| grep -v grep | awk '{print $2}'",
                shell=True, stdout=subprocess.PIPE
            )
            stdout_list, _ = p.communicate()
            stdout_list = stdout_list.split('\n')
            stdout_list.remove('')
            return stdout_list

        def run_whoami():
            p = subprocess.Popen("whoami", shell=True, stdout=subprocess.PIPE)
            whoami, _ = p.communicate()
            whoami = whoami.strip('\n')
            return whoami

        for pid in run_psx():
            try:
                filepath.os.kill(int(pid), signal.SIGINT)
            except:
                pass

            time.sleep(0.5)

        if run_whoami() == 'root':
            try:
                p = subprocess.Popen(
                    "sudo service transmission-daemon status",
                    shell=True, stdout=subprocess.PIPE,
                )
                response, error = p.communicate()
                if 'transmission-daemon start/running' in response:
                    p = subprocess.Popen(
                        "sudo service transmission-daemon stop",
                        shell=True, stdout=subprocess.PIPE,
                    )
                    output, error = p.communicate()

                    if error is not None and error is not '':
                        raise RuntimeError(error)
            except:
                log.err('Sudo access needed')
                raise

        log.err('All old transmission daemons killed')
        time.sleep(0.5)
