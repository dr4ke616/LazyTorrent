# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: TVShow
    :platform: Unix Windows
    :synopsis: TVShow model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

import datetime

from mamba.enterprise import Int, DateTime, Storm, Unicode
from mamba.application import model
from storm.references import Reference

from torrent_queue import TorrentQueue


class TVShow(model.Model, Storm):
    """
    TVShow model
    """

    __metaclass__ = model.MambaStorm
    __storm_table__ = 'tv_shows'
    __mamba_schema__ = False

    __media_type__ = 'TV_SHOW'

    tv_show_id = Int(primary=True, size=10, auto_increment=True)
    torrent_queue_id = Int(size=10)
    name = Unicode(size=256)
    season_number = Int(size=11)
    episode_number = Int(size=11)
    air_date = DateTime()
    episode_name = Unicode()
    rating = Int(size=11)

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

    def create(self, download_when=None):
        """Creates instance of tv show in database"""

        if download_when is None:
            if self.air_date is not None:
                one_day = datetime.timedelta(days=1)
                download_when = self.air_date + one_day
            else:
                download_when = datetime.datetime.now()

        if self.season_number < 10:
            sn = '0' + unicode(self.season_number)
        else:
            sn = unicode(self.season_number)

        if self.episode_number < 10:
            en = '0' + unicode(self.episode_number)
        else:
            en = unicode(self.episode_number)

        query = '{0} S{1}E{2}'.format(self.name, sn, en)

        print('TIME: {}'.format(download_when))
        self.torrent_queue_id = self._add_to_queue(download_when, query)

        store = self.database.store()
        store.add(self)
        store.commit()

    @classmethod
    def load(cls, **kwargs):
        store = cls.database.store()
        result = store.find(cls, **kwargs)
        return [queue for queue in result]

    def _add_to_queue(self, download_when, query):
        queue = TorrentQueue()
        queue.media_type = self.__media_type__
        queue.query = unicode(query)
        queue.download_when = download_when
        queue.status = u'PENDING'
        queue.date_added = datetime.datetime.now()
        queue.create()

        return queue.torrent_queue_id
