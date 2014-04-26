# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: TorrentQueue
    :platform: Unix Windows
    :synopsis: TorrentQueue model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

from datetime import datetime

from mamba.enterprise import (
    Int, DateTime, Storm, NativeEnum, Unicode, transact
)

from mamba.application import model


class TorrentQueue(model.Model, Storm):
    """
    TorrentQueue model
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'torrent_queue'

    id = Int(primary=True, size=11, auto_increment=True)
    media_type = NativeEnum(set={'MOVIE', 'TV_SHOW'})
    query = Unicode(size=256)
    download_when = DateTime()
    status = NativeEnum(
        set={
            'PENDING', 'FOUND', 'NOT_FOUND', 'FINISHED',
            'DOWNLOADING', 'WATCHED', 'DELETED'
        }
    )
    date_added = DateTime()
    torrent_hash = Unicode(size=256, default=None)

    def __init__(self, **kwargs):
        super(TorrentQueue, self).__init__()

        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                if type(value) == str:
                    value = unicode(value)

                setattr(self, key, value)

    def create(self):
        store = self.database.store()
        store.add(self)
        store.commit()

    def update_value(self, **kwargs):
        """ Updates a given value using the id """

        result = TorrentQueue.find(
            TorrentQueue.id == self.id, async=False
        ).one()

        for key, value in kwargs.iteritems():
            if hasattr(result, key):
                if type(value) == str:
                    value = unicode(value)

                setattr(result, key, value)

        result.update()
        self = result

    @classmethod
    @transact
    def update_status(cls, new_status, **kwargs):
        """Updates the status of a given torrent"""

        store = cls.database.store()

        result = store.find(cls, **kwargs)
        for r in result:
            r.status = new_status
        store.commit()

    @classmethod
    def load(cls, **kwargs):
        """Loads instance of torrent queue from db"""

        limit = kwargs.pop('limit', None)

        store = cls.database.store()
        result = store.find(cls, **kwargs)

        if limit is not None:
            result.config(limit=limit)

        return [queue for queue in result]

    @classmethod
    @transact
    def load_pending_queue(cls, **kwargs):
        """Loads all the pending torrent requests"""

        limit = kwargs.pop('limit', 5)
        store = cls.database.store()
        result = store.find(
            cls,
            cls.download_when <= datetime.now(),
            cls.status == 'PENDING',
            **kwargs
        )
        result.config(limit=limit)
        return [queue for queue in result]
