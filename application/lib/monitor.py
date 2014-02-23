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
from downloader import Downloader

from ..model.torrent_queue import TorrentQueue
from ..model.tv_show import TVShow
from ..model.movie import Movie


class TorrentMonitor(borg.Borg):

    def __init__(self):
        super(TorrentMonitor, self).__init__()
        if not hasattr(self, 'initialized'):
            self.initialized = False

        self.app = config.Application()
        self.initialize()

    def initialize(self, _=None, force=False):
        if not self.initialized or force:
            host = "http://{}".format(self.app.pirate_bay['host'])
            print 'Test Host: ', host
            print 'Is initialized ', self.initialized

            self.pirate_bay_client = ThePirateBay(host)
            self.downloader = Downloader(self.app.pirate_bay['torrent_host'])

            self.torrent_loop = task.LoopingCall(
                self.search_for_torrents
            )

            self.update_download_loop = task.LoopingCall(
                self.update_download_flag
            )

            deferreds = [
                self.torrent_loop.start(
                    self.app.pirate_bay['get_torrent']
                ),
                self.update_download_loop.start(
                    self.app.pirate_bay['update_download']
                )
            ]

            for d in deferreds:
                d.addErrback(self.initialize)

        if not self.initialized:
            self.initialized = True

    def update_download_flag(self):
        log.msg('Checking if we can download anything')
        Movie.can_we_download()
        TVShow.can_we_download()

    def search_for_torrents(self):
        log.msg('Searching for my torrents')

        ## TODO: Check database for new torrent requests
        torrents = TorrentQueue.get_queue(download_now=True)

        for torrent in torrents:
            req = self.pirate_bay_client.search(torrent.query)
            req.load_torrents(
                callback=self.on_torrents_found,
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
            return

        self.downloader.get(
            files_to_download=torrent_queue,
            on_file_created=self.file_created)

    def file_created(self, filename, file_id):
        log.msg('Saved file for torrent_queue_id: {}'.format(file_id))
        log.msg('Torrent saved at: {}'.format(filename))
        TorrentQueue.update_status(file_id, 'FOUND')

    def process_error(self, failure):
        log.err(str(failure))
        log.err(failure.getTraceback())
