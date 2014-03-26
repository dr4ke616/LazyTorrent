# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: TorrentQueue
    :platform: Unix Windows
    :synopsis: TorrentQueue model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

from datetime import datetime

from mamba.enterprise import Int, DateTime, Storm, NativeEnum, Unicode
from mamba.application import model


class TorrentQueue(model.Model, Storm):
    """
    TorrentQueue model
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'torrent_queue'
    __mamba_schema__ = False

    torrent_queue_id = Int(primary=True, size=10, auto_increment=True)
    media_type = NativeEnum(set={'MOVIE', 'TV_SHOW'})
    query = Unicode(size=256)
    download_when = DateTime(default=datetime.now())
    status = NativeEnum(set={'PENDING', 'FOUND', 'NOT_FOUND', 'FINISHED'})
    date_added = DateTime()

    def __init__(self, **kwargs):

        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                if type(value) == str:
                    value = unicode(value)

                setattr(self, key, value)

    def create(self):
        store = self.database.store()
        store.add(self)
        store.commit()

    @classmethod
    def load(cls, **kwargs):
        store = cls.database.store()
        result = store.find(cls, **kwargs)
        return [queue for queue in result]

    @classmethod
    def load_pending_queue(cls):
        store = cls.database.store()
        result = store.find(
            cls,
            cls.download_when <= datetime.now(),
            cls.status == 'PENDING'
        )
        return [queue for queue in result]

    @classmethod
    def update_status(cls, new_status, **kwargs):
        store = cls.database.store()

        result = store.find(cls, **kwargs)
        for r in result:
            r.status = new_status
        store.commit()
