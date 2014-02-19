# This file is part of auto_torrent
# Copyright (c) 2014 - Adam Drakeford <adamdrakeford@gmail.com>
# -*- coding: utf-8 -*-
"""
.. module:: Auto Torrent Downloader
    :platform: Unix, Windows
    :synopsis: Auto Torrent Downloader

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""


from twisted.web import server
from twisted.application import service

from mamba import Mamba
from mamba.web import Page

# from application.lib.tpb_client import ThePirateBayClient
from application.lib import test


def MambaApplicationFactory(settings):
    # create the application multi service
    application = service.MultiService()
    application.setName(settings.name)

    # register settings through Mamba Borg
    app = Mamba(settings)

    # create the root page
    root = Page(app)

    # create the site
    mamba_app_site = server.Site(root)

    # pb_client = ThePirateBayClient()
    # pb_client.initialize()
    # pb_client.send_request()
    test.test_pb()

    return mamba_app_site, application
