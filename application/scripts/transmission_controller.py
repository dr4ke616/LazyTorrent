#!/usr/bin/env python
"""
.. script:: transmission_controller
    :synopsis: Starts up and shuts down transmission programmily

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import sys
import signal
import time
import subprocess

from twisted.python import filepath


def handle_start():
    """ Starts the transmission daemon """

    if filepath.exists('transmission.pid'):
        print(
            'error: transmission.pid found, seems like the application is '
            'running already. If the application is not running, please '
            'delete transmission.pid and try again'
        )
        sys.exit(-1)

    p = subprocess.Popen(['transmission-daemon'])
    output, error = p.communicate()
    print('Starting transmission daemon')

    if error is not None and error is not '':
        raise RuntimeError(error)

    print('Transmission daemon started...')
    time.sleep(0.5)


def handle_stop():
    """ Kills the transmission daemon """

    transmission_pid = filepath.FilePath('transmission.pid')
    if not transmission_pid.exists():
        print('error: transmission.pid file can\'t be found.')
        sys.exit(-1)

    pid = transmission_pid.open().read()
    print('Killing process id {} with SIGINT signal'.format(pid))
    try:
        filepath.os.kill(int(pid), signal.SIGINT)
    except:
        raise

    print('Killed Transmission daemon {}...'.format(pid))
    time.sleep(0.5)


def kill_daemons():
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
            print('Sudo access needed')
            raise

    print('All old transmission daemons killed')
    time.sleep(0.5)


def main():
    # handle_start(False)
    handle_stop()
    # kill_daemons()


if __name__ == '__main__':
    main()
