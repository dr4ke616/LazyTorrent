# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: TorrentQueue
    :platform: Unix Windows
    :synopsis: TorrentQueue model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

from mamba.enterprise import Int, DateTime, Storm, NativeEnum, Unicode, Bool
from mamba.application import model


class TorrentQueueModelError(Exception):
    """Base exception class for model errors
    """


def required(obj, attr, value):
    if value is None:
        raise TorrentQueueModelError('{0}: required value'.format(attr))

    return value


class TorrentQueue(model.Model, Storm):
    """
    TorrentQueue model
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'torrent_queue'
    __mamba_schema__ = False

    torrent_queue_id = Int(
        primary=True, size=10, auto_increment=True, validator=required
    )
    media_type = NativeEnum(
        set={'MOVIE', 'TV_SHOW'}, validator=required
    )
    query = Unicode(size=256, validator=required)
    download_now = Bool(default=True, validator=required)
    status = NativeEnum(
        set={'PENDING', 'FOUND', 'FINISHED'}, validator=required
    )
    date_added = DateTime(validator=required)

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
    def get_queue(cls, download_now):
        store = cls.database.store()
        result = store.find(
            cls,
            cls.download_now == download_now
        )
        return [queue for queue in result]
