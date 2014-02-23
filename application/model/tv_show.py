# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: TVShow
    :platform: Unix Windows
    :synopsis: TVShow model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

from datetime import datetime

from mamba.enterprise import Int, DateTime, Storm, Unicode
from mamba.application import model
from storm.references import Reference
from base import required

from torrent_queue import TorrentQueue


class TVShow(model.Model, Storm):
    """
    TVShow model
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'tv_shows'
    __mamba_schema__ = False
    __media_type__ = 'TV_SHOW'

    tv_show_id = Int(
        primary=True, size=10, auto_increment=True, validator=required
    )
    torrent_queue_id = Int(size=10, validator=required)
    name = Unicode(size=256, validator=required)
    season_number = Int(validator=required)
    episode_number = Int(validator=required)
    air_date = DateTime()
    episode_name = Unicode(size=256)
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
        query = '{0} S{1}E{2}'.format(
            self.name,
            self.season_number,
            self.episode_number
        )

        queue = TorrentQueue(
            media_type=self.__media_type__,
            query=query,
            download_now=download_now,
            status='PENDING',
            date_added=datetime.now()
        )
        queue.create()
        self.torrent_queue_id = queue.torrent_queue_id

        store = self.database.store()
        store.add(self)
        store.commit()
