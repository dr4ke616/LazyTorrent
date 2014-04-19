 # Copyright (c) 2014 - Adam Drakeford <adam.drakeford@gmail.com>

"""
.. module:: webclient
    :platform: Unix, Windows
    :synopsis: Web client for BetBright WebServices

.. moduleauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

from urlparse import urlparse

from twisted.python import log
from twisted.internet import reactor
from twisted.web.http_headers import Headers
from twisted.web.client import Agent, ProxyAgent
from twisted.internet.endpoints import TCP4ClientEndpoint

from mamba.utils import config
from txsocksx.client import SOCKS5ClientEndpoint


def request(method, url, headers, producer=None, use_tor=False):
    """Make a HTTP request and returns a deferred
    """

    if use_tor:
        host = urlparse(url).netloc
        port = config.Application().tor_socks_port
        proxy = TCP4ClientEndpoint(reactor, "localhost", int(port))
        agent = ProxyAgent(SOCKS5ClientEndpoint(host, 80, proxy))
    else:
        agent = Agent(reactor)

    if headers is None:
        headers = Headers({'User-Agent': ['Twisted Web Client']})

    log.msg('Using TOR network' if use_tor else 'Using standard network')
    log.msg('Request URL: {}'.format(url))
    return agent.request(method, url, headers, producer)


def post(url, headers, producer=None, use_tor=False):
    """Make a POST HTTP request and returns a deferred
    """

    return request('POST', url, headers, producer, use_tor=use_tor)


def get(url, headers, producer=None, use_tor=False):
    """Make a GET HTTP request and returns a deferred
    """

    return request('GET', url, producer, use_tor=use_tor)


def put(url, headers, producer=None, use_tor=False):
    """Make a PUT request and returns a deferred
    """

    return request('PUT', url, producer, use_tor=use_tor)


def delete(url, headers, producer=None, use_tor=False):
    """Make a DELETE request and returns a deferred
    """

    return request('DELETE', url, producer, use_tor=use_tor)


def options(url, headers, producer=None, use_tor=False):
    """Make an OPTIONS request and returns a deferred
    """

    return request('OPTIONS', url, producer, use_tor=use_tor)


def patch(url, headers, producer=None, use_tor=False):
    """Make a PATCH request and returns a deferred
    """

    return request('PATCH', url, producer, use_tor)


def head(url, headers, producer=None, use_tor=False):
    """Make a HEAD request and returns a deferred
    """

    return request('HEAD', url, producer, use_tor)
