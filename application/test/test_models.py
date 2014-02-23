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
            'download_now': True,
            'status': 'PENDING',
            'date_added': datetime.now()
        }

        TorrentQueue(**params).create()
        queue = TorrentQueue.get_queue(download_now=True)
        self.assertEquals(1, len(queue))

    def test_movie(self):
        params = {
            'name': 'Titanic',
            'dvd_release': datetime.strptime('1989-08-17', '%Y-%m-%d'),
            'theater_release': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'rating': 10
        }
        Movie(**params).create(download_now=True)
        queue = TorrentQueue.get_queue(download_now=True)
        self.assertEquals(1, len(queue))

        movie = Movie.load(movie_id=1)
        self.assertEquals(1, len(movie))

        movie = Movie.load_after_dvd_release()
        self.assertEquals(1, len(movie))

        Movie.can_we_download()

    def test_tv_show(self):
        params = {
            'name': 'The Walking Dead',
            'season_number': 4,
            'episode_number': 10,
            'air_date': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'episode_name': 'The Walking Dead',
            'rating': 10
        }
        TVShow(**params).create(download_now=False)

        queue = TorrentQueue.get_queue(download_now=False)
        self.assertEquals(1, len(queue))

        tv_shows = TVShow.load(tv_show_id=1)
        self.assertEquals(1, len(tv_shows))

        TVShow.can_we_download()

    def test_add_loads(self):
        tv_params = {
            'name': 'The Walking Dead',
            'season_number': 4,
            'episode_number': 10,
            'air_date': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'episode_name': 'The Walking Dead',
            'rating': 10
        }
        TVShow(**tv_params).create(download_now=False)

        tv_params = {
            'name': 'The Walking Dead',
            'season_number': 4,
            'episode_number': 9,
            'air_date': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'episode_name': 'The Walking Dead',
            'rating': 10
        }
        TVShow(**tv_params).create(download_now=False)

        tv_params = {
            'name': 'The Walking Dead',
            'season_number': 4,
            'episode_number': 8,
            'air_date': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'episode_name': 'The Walking Dead',
            'rating': 10
        }
        TVShow(**tv_params).create(download_now=False)

        tv_params = {
            'name': 'The Walking Dead',
            'season_number': 4,
            'episode_number': 7,
            'air_date': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'episode_name': 'The Walking Dead',
            'rating': 10
        }
        TVShow(**tv_params).create(download_now=False)

        tv_params = {
            'name': 'The Walking Dead',
            'season_number': 4,
            'episode_number': 6,
            'air_date': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'episode_name': 'The Walking Dead',
            'rating': 10
        }
        TVShow(**tv_params).create(download_now=False)

        movie_params = {
            'name': 'Titanic',
            'dvd_release': datetime.strptime('1989-08-17', '%Y-%m-%d'),
            'theater_release': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'rating': 10
        }
        Movie(**movie_params).create(download_now=False)

        movie_params = {
            'name': 'Iron Man',
            'dvd_release': datetime.strptime('1989-08-17', '%Y-%m-%d'),
            'theater_release': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'rating': 10
        }
        Movie(**movie_params).create(download_now=False)

        movie_params = {
            'name': 'Superman',
            'dvd_release': datetime.strptime('1989-08-17', '%Y-%m-%d'),
            'theater_release': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'rating': 10
        }
        Movie(**movie_params).create(download_now=False)

        movie_params = {
            'name': 'Transformers',
            'dvd_release': datetime.strptime('1989-08-17', '%Y-%m-%d'),
            'theater_release': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'rating': 10
        }
        Movie(**movie_params).create(download_now=False)

        movie_params = {
            'name': 'Lord of the rings',
            'dvd_release': datetime.strptime('1989-08-17', '%Y-%m-%d'),
            'theater_release': datetime.strptime('1990-08-17', '%Y-%m-%d'),
            'rating': 10
        }
        Movie(**movie_params).create(download_now=False)
