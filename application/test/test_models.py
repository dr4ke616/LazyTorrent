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

    def test_torrent_queue(self):
        params = {
            'media_type': 'MOVIE',
            'query': 'Titanic',
            'force_download': True,
            'status': 'PENDING',
            'date_added': datetime.now()
        }

        TorrentQueue(**params).create()
        queue = TorrentQueue.get_queue(force_download=True)
        self.assertEquals(1, len(queue))

    def test_movie(self):
        params = {
            'name': 'Titanic',
            'dvd_release': datetime.strptime('1989-08-17', '%Y-%m-%d'),
            'theater_release': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'rating': 10
        }
        Movie(**params).create(force_download=True)
        queue = TorrentQueue.get_queue(force_download=True)
        self.assertEquals(1, len(queue))

    def test_tv_show(self):
        params = {
            'name': 'The Walking Dead',
            'season_number': 1,
            'episode_number': 13,
            'air_date': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'episode_name': 'The Walking Dead',
            'rating': 10
        }
        TVShow(**params).create(force_download=False)
        queue = TorrentQueue.get_queue(force_download=False)
        self.assertEquals(1, len(queue))
