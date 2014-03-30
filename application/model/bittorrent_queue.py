# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: BittorrentQueue
    :platform: Unix Windows
    :synopsis: BittorrentQueue model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

from mamba.enterprise import Int, Storm, Unicode
from mamba.application import model


class BittorrentQueue(model.Model, Storm):
    """
    BittorrentQueue model
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'bittorrent_queue'
    __mamba_schema__ = False

    id = Int(primary=True, size=11, auto_increment=True)
    client_id = Int(size=11)
    torrent_id = Int(size=11)
    torrent_queue_id = Int(size=11)
    name = Unicode(size=256)
    url = Unicode()

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                if type(value) == str:
                    value = unicode(value)

                setattr(self, key, value)

    def create(self):
        """Creates instance of tv show in database"""

        store = self.database.store()
        store.add(self)
        store.commit()

    @classmethod
    def load(cls, **kwargs):
        store = cls.database.store()
        result = store.find(cls, **kwargs)
        return [queue for queue in result]
