# -*- coding: utf-8 -*-
"""
.. module:: TorrentMonitor
    :synopsis: Checks torrent database for new torrent requests

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from datetime import datetime

from mamba.utils import borg, config
from twisted.internet import task
from twisted.python import log

from the_pirate_bay.tpb import ThePirateBay
from downloader import Downloader

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
                self.process_torrent_request
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

    def process_torrent_request(self):
        now = datetime.now()
        log.msg('process_torrent_request {0}'.format(now))

        ## TODO: Check database for new torrent requests
        torrent_request = True
        torrent_query = 'The Walking Dead'

        if torrent_request:
            req = self.pirate_bay_client.search(torrent_query)
            req.load_torrents(callback=self.on_torrents_found)

    def on_torrents_found(self, torrents):
        torrent_queue = tuple()

        if len(torrents) > 0:
            chunks = torrents[0].torrent_link_chunks
            remote_file = '{}/{}'.format(chunks['id'], chunks['url-title'])
            location = self.app.torrent_destination + chunks['url-title']

            file_to_get = {
                'remote_file': remote_file,
                'location': location
            }
            torrent_queue += (file_to_get, )
        else:
            print 'No Torrents found'
            return

        self.downloader.get(torrent_queue, on_file_created=self.file_created)

    def file_created(self, filename):
        print 'Torrent saved at: ', filename

    def process_error(self, failure):
        log.err(str(failure))
        log.err(failure.getTraceback())
