# -*- coding: utf-8 -*-

"""
.. module:: startup
    :synopsis: Startup module for checking conflicting processes
        running on system

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""


from twisted.python import log
from twisted.internet import defer
from twisted.internet import reactor, utils


@defer.inlineCallbacks
def kill_transmission():

    output = yield utils.getProcessOutput(
        'service', ['transmission-daemon', 'stop']
    )
    log.msg(output)
    print(output)


@defer.inlineCallbacks
def kill_tor():

    output = yield utils.getProcessOutput(
        'service', ['tor', 'stop']
    )
    log.msg(output)
    print(output)


def whoami():
    return utils.getProcessOutput('whoami')


@defer.inlineCallbacks
def check_conflicting_process(auto_kill):

    _kill_tor = False
    _kill_transmission = False

    output = yield utils.getProcessOutput("ps", ["aux"])
    lines = output.splitlines()
    for line in lines:
        if 'tor ' in line:
            _kill_tor = True
        if 'transmission-daemon ' in line:
            _kill_transmission = True

    if not auto_kill:
        msg = None
        if _kill_tor and _kill_transmission:
            msg = 'Tor and Transmission daemons are'
        elif _kill_tor:
            msg = 'Tor daemon is'
        elif _kill_transmission:
            msg = 'Transmission daemon is'

        if msg is not None:
            message = 'running. It is recomanded that you kill them before starting Lazy Torrent'
            log.err('{} {} '.format(msg, message))
            raise RuntimeError('{} {}'.format(msg, message))

    else:
        _whoami = yield whoami()
        _whoami = _whoami.strip('\n')

        if _whoami != 'root':
            raise RuntimeError('You need to be root to kill other daemons')

        if _kill_tor:
            kill_tor()
        elif _kill_transmission:
            kill_transmission()

    log.msg('Everything OK')
    print('Everything OK')


if __name__ == '__main__':
    check_conflicting_process(True)
    reactor.run()
