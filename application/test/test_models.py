# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: ModelsTestCase
    :platform: Unix Windows
    :synopsis: ModelsTestCase model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

from datetime import datetime

import unittest

from ..model.torrent_queue import TorrentQueue
from ..model.tv_show import TVShow
from ..model.movie import Movie


class ModelsTestCase(unittest.TestCase):

    def setUp(self):
        ## Tear down databse and create schema
        store = TorrentQueue.database.store()
        store.execute("SET FOREIGN_KEY_CHECKS=0;")
        store.execute("TRUNCATE TABLE torrent_queue;")
        store.execute("TRUNCATE TABLE movies;")
        store.execute("TRUNCATE TABLE tv_shows;")
        store.execute("SET FOREIGN_KEY_CHECKS=1;")
        store.commit()

    def test_torrent_queue_no_when(self):
        queue = TorrentQueue()
        queue.media_type = u'MOVIE'
        queue.query = u'Titanic'
        queue.status = u'PENDING'
        queue.date_added = datetime.now()
        queue.create()

        queue = TorrentQueue.load()
        self.assertEquals(1, len(queue))

    def test_torrent_queue_with_when(self):
        queue = TorrentQueue()
        queue.media_type = u'MOVIE'
        queue.query = u'Titanic'
        queue.download_when = datetime.now()
        queue.status = u'PENDING'
        queue.date_added = datetime.now()
        queue.create()

        queue = TorrentQueue.load()
        self.assertEquals(1, len(queue))

    def test_movie_no_when(self):
        movie = Movie()
        movie.name = u'Titanic'
        movie.dvd_release = datetime.strptime('1989-08-17', '%Y-%m-%d')
        movie.theater_release = datetime.strptime('1989-02-17', '%Y-%m-%d')
        movie.rating = 9
        movie.create()

        queue = TorrentQueue.load()
        self.assertEquals(1, len(queue))

        movie = Movie.load(movie_id=1)
        self.assertEquals(1, len(movie))

    def test_movie_with_when(self):
        movie = Movie()
        movie.name = u'Titanic'
        movie.dvd_release = datetime.strptime('1989-08-17', '%Y-%m-%d')
        movie.theater_release = datetime.strptime('1989-02-17', '%Y-%m-%d')
        movie.rating = 9
        movie.create()

        queue = TorrentQueue.load_pending_queue()
        self.assertEquals(1, len(queue))

        movie = Movie.load(movie_id=1)
        self.assertEquals(1, len(movie))

    def test_movie_with_when_before_release_date(self):
        movie = Movie()
        movie.name = u'Titanic'
        movie.dvd_release = datetime.strptime('2089-08-17', '%Y-%m-%d')
        movie.theater_release = datetime.strptime('2089-02-17', '%Y-%m-%d')
        movie.rating = 9
        movie.create()

        queue = TorrentQueue.load_pending_queue()
        self.assertEquals(0, len(queue))

        movie = Movie.load(movie_id=1)
        self.assertEquals(1, len(movie))

    def test_tv_show_no_when(self):
        tv_show = TVShow()
        tv_show.name = u'The Walking Dead'
        tv_show.season_number = 4
        tv_show.episode_number = 10
        tv_show.air_date = datetime.strptime('1989-08-17', '%Y-%m-%d')
        tv_show.episode_name = u'TWD'
        tv_show.rating = 9
        tv_show.create()

        queue = TorrentQueue.load()
        self.assertEquals(1, len(queue))

        tv_show = TVShow.load(tv_show_id=1)
        self.assertEquals(1, len(tv_show))

    def test_tv_show_with_when(self):
        tv_show = TVShow()
        tv_show.name = u'The Walking Dead'
        tv_show.season_number = 4
        tv_show.episode_number = 10
        tv_show.air_date = datetime.strptime('1989-08-17', '%Y-%m-%d')
        tv_show.episode_name = u'TWD'
        tv_show.rating = 9
        tv_show.create()

        queue = TorrentQueue.load_pending_queue()
        self.assertEquals(1, len(queue))

        tv_show = TVShow.load(tv_show_id=1)
        self.assertEquals(1, len(tv_show))

    def test_tv_show_with_when_before_air_date(self):
        tv_show = TVShow()
        tv_show.name = u'The Walking Dead'
        tv_show.season_number = 4
        tv_show.episode_number = 10
        tv_show.air_date = datetime.strptime('2089-08-17', '%Y-%m-%d')
        tv_show.episode_name = u'TWD'
        tv_show.rating = 9
        tv_show.create()

        queue = TorrentQueue.load_pending_queue()
        self.assertEquals(0, len(queue))

        tv_show = TVShow.load(tv_show_id=1)
        self.assertEquals(1, len(tv_show))
