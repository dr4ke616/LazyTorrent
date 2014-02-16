# This file is part of torrent
# Copyright (c) ${year} - adam <adam@localhost>

"""
.. module:: torrent
    :platform: Unix, Windows
    :synopsis: Torrent

.. moduleauthor:: adam <adam@localhost>
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
