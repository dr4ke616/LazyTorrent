# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: Movie
    :platform: Unix Windows
    :synopsis: Movie model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

from datetime import datetime

from mamba.enterprise import Int, DateTime, Storm, Unicode
from mamba.application import model
from storm.references import Reference

from torrent_queue import TorrentQueue


class MovieModelError(Exception):
    """Base exception class for model errors
    """


def required(obj, attr, value):
    if value is None:
        raise MovieModelError('{0}: required value'.format(attr))

    return value


class Movie(model.Model, Storm):
    """
    Movie model
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'movies'
    __mamba_schema__ = False
    __media_type__ = 'MOVIE'

    movie_id = Int(
        primary=True, size=10, auto_increment=True, validator=required
    )
    torrent_queue_id = Int(size=10, validator=required)
    name = Unicode(size=256, validator=required)
    dvd_release = DateTime()
    theater_release = DateTime()
    rating = Int()

    # references
    torrent_queue = Reference(
        torrent_queue_id, 'TorrentQueue.torrent_queue_id'
    )

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                if type(value) == str:
                    value = unicode(value)

                setattr(self, key, value)

    def create(self, download_now):
        queue = TorrentQueue(
            media_type=self.__media_type__,
            query=self.name,
            download_now=download_now,
            status='PENDING',
            date_added=datetime.now()
        )
        queue.create()
        self.torrent_queue_id = queue.torrent_queue_id

        store = self.database.store()
        store.add(self)
        store.commit()
