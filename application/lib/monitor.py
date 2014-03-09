# -*- coding: utf-8 -*-
"""
.. module:: TorrentMonitor
    :synopsis: Checks torrent database for new torrent requests

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from mamba.utils import borg, config
from twisted.internet import task
from twisted.python import log

from the_pirate_bay.tpb import ThePirateBay
from the_pirate_bay.constants import *
from downloader import Downloader

from ..model.torrent_queue import TorrentQueue
from ..model.tv_show import TVShow
from ..model.movie import Movie


class TorrentMonitor(borg.Borg):

    retry_count = 0
    host_index = 0

    def __init__(self):
        super(TorrentMonitor, self).__init__()
        if not hasattr(self, 'initialized'):
            self.initialized = False

        self.app = config.Application()
        self.initialize()

    def initialize(self, _=None, force=False):
        self._initialize_hosts()

        if not self.initialized or force:

            self.torrent_loop = task.LoopingCall(
                self.search_for_torrents
            )

            self.update_download_loop = task.LoopingCall(
                self.update_download_flag
            )

            deferreds = [
                self.torrent_loop.start(
                    self.app.monitor_torrent
                ),
                self.update_download_loop.start(
                    self.app.monitor_download
                )
            ]

            for d in deferreds:
                d.addErrback(self.initialize)

        if not self.initialized:
            self.initialized = True

    def _initialize_hosts(self):

        log.msg('Retry count: {}'.format(self.retry_count))
        max_retries = self.app.max_retries

        if self.retry_count == max_retries or not self.initialized:
            self.retry_count = 0

            hosts = self.app.pirate_bay_hosts

            host_config = hosts[self.host_index]
            web_host = "http://{}".format(host_config['host'])
            torrent_host = host_config['torrent_host']
            use_tor = host_config['use_tor_network']

            self.pirate_bay_client = ThePirateBay(web_host, use_tor)
            self.downloader = Downloader(torrent_host, use_tor)

            log.msg('Switching to different host')

            self.host_index += 1
            if self.host_index == len(hosts):
                self.host_index = 0
        else:
            self.retry_count += 1

    def update_download_flag(self):
        log.msg('Checking if we can download anything')
        Movie.can_we_download()
        TVShow.can_we_download()

    def search_for_torrents(self):
        log.msg('Searching for my torrents')

        torrents = TorrentQueue.get_queue(download_now=True)

        for torrent in torrents:
            req = self.pirate_bay_client.search(
                query=torrent.query,
                order=ORDERS.SEEDERS.DES,
                category=CATEGORIES.VIDEO.ALL
            )

            req.load_torrents(
                callback=self.on_torrents_found,
                errback=self.error_finding_torrents,
                db_id=torrent.torrent_queue_id
            )

    def on_torrents_found(self, torrents, db_id):
        torrent_queue = tuple()

        if len(torrents) > 0:
            log.msg('Torrent found for torrent_queue_id: {}'.format(db_id))

            chunks = torrents[0].torrent_link_chunks
            remote_file = '{}/{}'.format(chunks['id'], chunks['url-title'])
            location = self.app.torrent_destination + chunks['url-title']

            file_to_get = {
                'remote_file': remote_file,
                'location': location,
                'id': db_id
            }
            torrent_queue += (file_to_get, )
        else:
            log.msg('No Torrents found for torrent_queue_id: {}'.format(db_id))
            TorrentQueue.update_status(db_id, 'NOT_FOUND')
            return

        self.downloader.get(
            files_to_download=torrent_queue,
            on_file_created=self.file_created,
            errback=self.error_finding_torrents)

    def error_finding_torrents(self):
        log.msg('Going to try again')
        self._initialize_hosts()

    def file_created(self, filename, file_id):
        log.msg('Saved file for torrent_queue_id: {}'.format(file_id))
        log.msg('Torrent saved at: {}'.format(filename))
        TorrentQueue.update_status(file_id, 'FOUND')
