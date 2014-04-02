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

from application.lib.monitor import TorrentMonitor


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

    TorrentMonitor()

    return mamba_app_site, application
