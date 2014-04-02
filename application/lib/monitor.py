# -*- coding: utf-8 -*-
"""
.. module:: TorrentMonitor
    :synopsis: Checks torrent database for new torrent requests

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import time

from twisted.python import log
from twisted.internet import task
from mamba.utils import borg, config
from zope.component import getUtility

from the_pirate_bay.constants import *
from the_pirate_bay.tpb import ThePirateBay
from download_manager import DownloadManager

from application.model.torrent_queue import TorrentQueue


class TorrentMonitor(borg.Borg):

    host_index = 0
    retry_count = 0

    def __init__(self):
        super(TorrentMonitor, self).__init__()
        if not hasattr(self, 'initialized'):
            self.initialized = False

        self.app = config.Application()
        self.download_manager = DownloadManager()

        self.initialize()

    def initialize(self):
        self._initialize_hosts()

        if not self.initialized:

            self.torrent_loop = task.LoopingCall(
                self.search_for_torrents
            )

            self.torrent_progress_loop = task.LoopingCall(
                self.download_manager.monitor_torrent_progress
            )

            self.retry_download_loop = task.LoopingCall(
                self.retry_download
            )

            deferreds = [
                self.torrent_loop.start(
                    self.app.monitor_torrent
                ),
                self.torrent_progress_loop.start(
                    self.app.torrent_progress
                ),
                self.retry_download_loop.start(
                    self.app.retry_download
                )
            ]

            for d in deferreds:
                d.addErrback(self._reconnect_stores)

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
            self.download_manager.initialize(torrent_host, use_tor, self.app)

            log.msg('Switching to different host')

            self.host_index += 1
            if self.host_index == len(hosts):
                self.host_index = 0
        else:
            self.retry_count += 1

    def retry_download(self):
        log.msg('Going to reset the statuses of NOT_FOUND items in queue')

        TorrentQueue.update_status(
            new_status='PENDING', status='NOT_FOUND'
        )

    def search_for_torrents(self):
        log.msg('Searching for my torrents')

        queue = TorrentQueue.load_pending_queue()

        for torrent in queue:
            req = self.pirate_bay_client.search(
                query=torrent.query,
                optimize_query=True,
                order=ORDERS.SEEDERS.DES,
                category=CATEGORIES.VIDEO.ALL
            )

            req.load_torrents(
                callback=self.on_torrents_found,
                errback=self.error_finding_torrents,
                db_id=torrent.torrent_queue_id
            )

    def on_torrents_found(self, torrents, db_id):
        """ Callback for reponse from pirate bay sites
            :param: list of torrents
            :param: the id refrencing the queue database table
        """

        if len(torrents) > 0:
            log.msg('Torrent found for torrent_queue_id: {}'.format(db_id))

            self.download_manager.download(torrents[0], db_id)
        else:
            log.msg('No Torrents found for torrent_queue_id: {}'.format(db_id))

            TorrentQueue.update_status(
                new_status='NOT_FOUND', torrent_queue_id=db_id
            )

    def error_finding_torrents(self):
        log.msg('Going to try again')
        self._initialize_hosts()

    def _reconnect_stores(self, error):
        """Reconnect all the stores if there is some problem
        """

        if error is not None:
            log.err('Whooops, detected an error with the database:')
            log.err(error)

        zstorm = getUtility(IZStorm)
        for name, store in zstorm.iterstores():
            if error is not None:
                log.msg('Reconnecting store {}...'.format(name))
            store.rollback()

        if not self.torrent_loop.running:
            time.sleep(0.5)
            d = self.torrent_loop.start(self.app.monitor_torrent)
            d.addErrback(self._reconnect_stores)

        if not self.torrent_progress_loop.running:
            time.sleep(0.5)
            d = self.torrent_progress_loop.start(self.app.torrent_progress)
            d.addErrback(self._reconnect_stores)

        if not self.retry_download_loop.running:
            time.sleep(0.5)
            d = self.retry_download_loop.start(self.app.retry_download)
            d.addErrback(self._reconnect_stores)

        self._initialize_hosts()
