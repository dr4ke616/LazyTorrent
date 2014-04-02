# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: ModelsTestCase
    :platform: Unix Windows
    :synopsis: ModelsTestCase model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

import os.path
import unittest
from datetime import datetime

from application.model.tv_show import TVShow
from application.lib.the_pirate_bay.utils import URL
from application.model.torrent_queue import TorrentQueue
from application.lib.the_pirate_bay.torrent import Torrent
from application.lib.download_manager import DownloadManager


class ModelsTestCase(unittest.TestCase):

    def setUp(self):
        self.location = "/home/adam/Downloads/auto_torrent/"
        self.torrent_host = "torrents.thepiratebay.se"
        self.use_tor = False

        ## Tear down databse and create schema
        store = TorrentQueue.database.store()
        sql = self._load_sql_schema()
        store.execute(sql)
        store.commit()

    def get_torrent(self, print_torrent=False):
        torrent_link = '''
            http://torrents.thepiratebay.se/9858200/The_Walking_Dead_S04E16_PROPER_HDTV_x264-2HD_[eztv].torrent
        '''

        url = URL(
            base='uberproxy.net',
            path='/search',
            segments=['query', 'page', 'order', 'category'],
            defaults=['The Walking Dead', '0', '7', '0']
        )

        kwargs = {
            'title': 'The.Walking.Dead.S04E16.REPACK',
            'url': url.build(),
            'category': 'video',
            'sub_category': 'tv show',
            'magnet_link': 'some url',
            'torrent_link': torrent_link,
            'created': '2014-04-01 01:04:28 GMT',
            'size': 'size',
            'user': 'user',
            'seeders': 10,
            'leechers': 10
        }

        torrent = Torrent(**kwargs)
        if print_torrent:
            torrent.print_torrent()

        return Torrent(**kwargs)

    def get_torrent_queue(self):
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

        return queue[0]

    def test_torrent_mock_object(self):
        torrent = self.get_torrent()
        self.assertEquals('user', torrent.user)

    def test_manual_download(self):
        queue = self.get_torrent_queue()
        torrent = self.get_torrent()

        dm = DownloadManager(
            self.torrent_host, queue.torrent_queue_id, self.use_tor
        )

        dm.download(torrent)
        check = self._check_file_exists(
            'The_Walking_Dead_S04E16_PROPER_HDTV_x264-2HD_[eztv].torrent'
        )
        self.assertTrue(check)

    def _check_file_exists(self, file_name):
        return os.path.isfile(self.location + file_name)

    def _load_sql_schema(slef):
        path = os.path.dirname(os.path.realpath(__file__))
        with open(path + '/../model/schema/db_schema.sql', 'r') as f:
            content = f.read()
            f.close()

        return content
