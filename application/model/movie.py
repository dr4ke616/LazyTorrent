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


class Movie(model.Model, Storm):
    """
    Movie model
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'movies'

    __media_type__ = 'MOVIE'

    id = Int(primary=True, size=11, auto_increment=True)
    torrent_queue_id = Int(size=11)
    name = Unicode(size=256)
    dvd_release = DateTime(default=None)
    theater_release = DateTime(default=None)
    rating = Int(default=None)

    # references
    torrent_queue = Reference(torrent_queue_id, 'TorrentQueue.id')

    def __init__(self, **kwargs):
        for key, value in kwargs.iteritems():
            if hasattr(self, key):
                if type(value) == str:
                    value = unicode(value)

                setattr(self, key, value)

    def create(self, download_when=None):
        """Creates instance of movie in database"""

        if download_when is None:
            if self.dvd_release is not None:
                delta = datetime.timedelta(hours=40)
                download_when = self.dvd_release + delta
            else:
                download_when = datetime.datetime.now()

        self.torrent_queue_id = self._add_to_queue(download_when)

        store = self.database.store()
        store.add(self)
        store.commit()

    @classmethod
    def load(cls, **kwargs):
        store = cls.database.store()
        result = store.find(cls, **kwargs)
        return [queue for queue in result]

    def _add_to_queue(self, download_when):
        queue = TorrentQueue()
        queue.media_type = self.__media_type__
        queue.query = self.name
        queue.download_when = download_when
        queue.status = u'PENDING'
        queue.date_added = datetime.datetime.now()
        queue.create()

        return queue.id
