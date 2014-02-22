# -*- coding: utf-8 -*-
"""
.. module:: WebClient
    :synopsis: Small wrapper for sending requests to website using Twisted
        over the tor network (optionally)

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

# monkey patch anoying noyse in XMLRPC Twisted client
from twisted.python.monkey import MonkeyPatcher
from twisted.web.client import _HTTP11ClientFactory
monkey_patch = MonkeyPatcher((_HTTP11ClientFactory, 'noisy', False))
monkey_patch.patch()

from txsocksx.client import SOCKS5ClientEndpoint

from twisted.web.client import Agent, readBody, ProxyAgent
from twisted.internet.endpoints import TCP4ClientEndpoint
from twisted.web.http_headers import Headers
from twisted.internet import defer, reactor
from twisted.python import log


class _WebClient(object):
    def __init__(self, host, use_tor):
        self._host = str(host)

        if use_tor:
            proxy = TCP4ClientEndpoint(reactor, "localhost", 9150)
            proxied_endpoint = SOCKS5ClientEndpoint(self._host, 80, proxy)
            self._agent = ProxyAgent(proxied_endpoint)
        else:
            self._agent = Agent(reactor)

    def request(self, path):
        url = 'http://{}/{}'.format(self._host, path)
        log.msg('URL: {}'.format(url))
        headers = Headers({'User-Agent': ['Twisted Web Client']})

        d = self._agent.request('GET', url, headers, None)
        d.addCallback(self.callback_request)
        d.addErrback(self.process_error)
        return d

    def read_body(self, body):
        return body

    def process_error(self, failure):
        log.err('There was an error')
        log.err(failure.printTraceback())

    def callback_request(self, response):
        log.msg('Response Code: {}'.format(response.code))

        d = readBody(response)
        d.addCallbacks(self.read_body)
        d.addErrback(self.process_error)
        return d


class WebClient(object):

    def __init__(self, host, use_tor=True):
        self._web_client = _WebClient(host, use_tor)

    @defer.inlineCallbacks
    def request_page(self, path):
        response = yield self._web_client.request(path)
        defer.returnValue(response)
