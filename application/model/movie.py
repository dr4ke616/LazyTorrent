# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: Movie
    :platform: Unix Windows
    :synopsis: Movie model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

import datetime

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
            date_added=datetime.datetime.now()
        )
        queue.create()
        self.torrent_queue_id = queue.torrent_queue_id

        store = self.database.store()
        store.add(self)
        store.commit()

    @classmethod
    def load(cls, **kwargs):
        store = cls.database.store()

        movie_id = kwargs.get('movie_id', None)
        torrent_queue_id = kwargs.get('torrent_queue_id', None)
        name = kwargs.get('name', None)
        dvd_release = kwargs.get('dvd_release', None)
        theater_release = kwargs.get('theater_release', None)
        rating = kwargs.get('rating', None)
        movies = None

        if movie_id is not None:
            movies = store.find(
                Movie,
                Movie.movie_id == movie_id
            )

        if torrent_queue_id is not None:
            movies = movies.find(
                Movie.torrent_queue_id == torrent_queue_id
            )

        if name is not None:
            movies = movies.find(
                Movie.name == name
            )

        if dvd_release is not None:
            movies = movies.find(
                Movie.dvd_release == dvd_release,
            )

        if theater_release is not None:
            movies = movies.find(
                Movie.theater_release == theater_release,
            )

        if rating is not None:
            movies = movies.find(
                Movie.rating == rating,
            )

        if movies is not None:
            return [movie for movie in movies]
        else:
            return None

    @classmethod
    def load_after_dvd_release(cls, date_from=None):
        store = cls.database.store()

        if date_from is None:
            now = datetime.datetime.now()
            date_from = now + datetime.timedelta(days=1)

        movies = store.find(
            Movie,
            Movie.dvd_release <= date_from
        )

        if movies is not None:
            return [movie for movie in movies]
        else:
            return None

    def update_download_flag(self, flag):
        store = self.database.store()
        torrent_queue = self.torrent_queue
        torrent_queue.download_now = flag
        store.commit()

    @classmethod
    def can_we_download(cls):
        movies = Movie.load_after_dvd_release()
        for movie in movies:
            movie.update_download_flag(True)
