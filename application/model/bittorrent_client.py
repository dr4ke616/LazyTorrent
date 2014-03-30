# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: BittorrentClient
    :platform: Unix Windows
    :synopsis: BittorrentClient model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

from mamba.enterprise import Int, Storm, Unicode
from mamba.application import model


class BittorrentClient(model.Model, Storm):
    """
    BittorrentClient model
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'bittorrent_clients'
    __mamba_schema__ = False

    client_id = Int(primary=True, size=11, auto_increment=True)
    description = Unicode(size=256)

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                if type(value) == str:
                    value = unicode(value)

                setattr(self, key, value)
