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


class TVShowModelError(Exception):
    """Base exception class for model errors
    """


def required(obj, attr, value):
    if value is None:
        raise TVShowModelError('{0}: required value'.format(attr))

    return value


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
        if self.season_number < 10:
            sn = '0' + unicode(self.season_number)
        else:
            sn = unicode(self.season_number)

        if self.episode_number < 10:
            en = '0' + unicode(self.episode_number)
        else:
            en = unicode(self.episode_number)

        query = '{0} S{1}E{2}'.format(self.name, sn, en)

        queue = TorrentQueue(
            media_type=self.__media_type__,
            query=query,
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

        tv_show_id = kwargs.get('tv_show_id', None)
        torrent_queue_id = kwargs.get('torrent_queue_id', None)
        name = kwargs.get('name', None)
        season_number = kwargs.get('season_number', None)
        episode_number = kwargs.get('episode_number', None)
        air_date = kwargs.get('air_date', None)
        episode_name = kwargs.get('episode_name', None)
        rating = kwargs.get('rating', None)
        tv_show = None

        if tv_show_id is not None:
            tv_show = store.find(
                TVShow,
                TVShow.tv_show_id == tv_show_id
            )

        if torrent_queue_id is not None:
            tv_show = tv_show.find(
                TVShow.torrent_queue_id == torrent_queue_id
            )

        if name is not None:
            tv_show = tv_show.find(
                TVShow.name == name
            )

        if season_number is not None:
            tv_show = tv_show.find(
                TVShow.season_number == season_number,
            )

        if episode_number is not None:
            tv_show = tv_show.find(
                TVShow.episode_number == episode_number,
            )

        if air_date is not None:
            tv_show = tv_show.find(
                TVShow.air_date == air_date,
            )

        if episode_name is not None:
            tv_show = tv_show.find(
                TVShow.episode_name == episode_name,
            )

        if rating is not None:
            tv_show = tv_show.find(
                TVShow.rating == rating,
            )

        if tv_show is not None:
            return [tvs for tvs in tv_show]
        else:
            return None

    @classmethod
    def load_after_air_date(cls, date_from=None):
        store = cls.database.store()

        if date_from is None:
            now = datetime.datetime.now()
            date_from = now + datetime.timedelta(days=1)

        tv_shows = store.find(
            TVShow,
            TVShow.air_date <= date_from
        )

        if tv_shows is not None:
            return [tvs for tvs in tv_shows]
        else:
            return None

    def update_download_flag(self, flag):
        store = self.database.store()
        torrent_queue = self.torrent_queue
        torrent_queue.download_now = flag
        store.commit()

    @classmethod
    def can_we_download(cls):
        tv_shows = TVShow.load_after_air_date()
        for tv_show in tv_shows:
            tv_show.update_download_flag(True)

