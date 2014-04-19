# -*- coding: utf-8 -*-
"""
.. module:: DownloadManager
    :synopsis: Checks torrent database for new torrent requests

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import os
import traceback
import transmissionrpc

from twisted.python import log
from mamba.utils import config

from downloader import Downloader
from application.model.movie import Movie
from application.model.tv_show import TVShow
from application.model.torrent_queue import TorrentQueue


def check_connection(func):

    def wrapper(*args, **kwargs):
        transmission_wrap = args[0]

        log.msg(
            'Testing connection to Transmission. Active: {}'
            .format(transmission_wrap.is_active)
        )

        try:
            if transmission_wrap.is_active:
                transmission_wrap._ping()
        except transmissionrpc.TransmissionError:
            log.msg('Lost connection to Transmission.')
            transmission_wrap.is_active = False

        return func(*args, **kwargs)

    return wrapper


class DownloadManager(object):

    def __init__(self):
        super(DownloadManager, self).__init__()

    def initialize(self, torrent_host, use_tor, app=None):
        self.app = app

        if self.app is None:
            self.app = config.Application('../../config/application.json')

        self.torrent_host = torrent_host
        self.use_tor = use_tor
        self.transmission = TransmissionWrapper(self.app)

    def download(self, torrent, queue_id):
        """ Handels the download request """

        if self.transmission.is_active:
            log.msg('TransmissionBT is running, lets use it.')
            self._handle_transmission(torrent, queue_id)
        else:
            log.msg(
                'No bit torrent client running, lets just download '
                'the torrent directly.'
            )
            self._handle_manual_download(torrent, queue_id)

    def _handle_transmission(self, torrent, queue_id):

        if torrent.magnet_link is not None:
            link = torrent.magnet_link
        elif torrent.torrent_link is not None:
            link = torrent.torrent_link
        else:
            self._handle_manual_download(torrent, queue_id)
            return

        directory = self._create_directory(queue_id)
        torrents = self.transmission.add_torrent(link, directory)

        torrent_queue = TorrentQueue(torrent_queue_id=queue_id)
        torrent_queue.update_value(
            status=u'FOUND', torrent_hash=torrents.hashString
        )

    def _handle_manual_download(self, torrent, queue_id):
        """ Handles the manual download. Dumps torrent file into
            dir specified in config
        """

        downloader = Downloader(self.use_tor)

        chunks = torrent.torrent_link_chunks
        url = 'http://{}/{}/{}'.format(
            self.torrent_host, chunks['id'], chunks['url-title']
        )
        download_location = self.app.torrent_destination + chunks['url-title']
        torrent_queue = ({
            'url': url,
            'download_location': download_location,
            'id': queue_id
        }, )

        downloader.get(
            files_to_download=torrent_queue,
            on_file_created=self.__file_created,
            errback=self.__error_finding_torrents
        )

    def monitor_torrent_progress(self):
        """ Monitor download of torrent progess. Used with torrent client
        """

        log.msg('Monitoring currently downloading torrents')

        torrent_queue = TorrentQueue.find(
            (TorrentQueue.status == u'FOUND') |
            (TorrentQueue.status == u'DOWNLOADING'),
            async=False
        )

        for tq in torrent_queue:

            if tq.torrent_hash is None:
                continue

            try:
                torrent = self.transmission.get_torrent(tq.torrent_hash)

                if torrent is None:
                    if self.transmission.is_active is False:
                        # Connection to Transmission has gone away.
                        # Setting state of torrent queue so that the torrent
                        # file can be downloaded manually

                        tq.torrent_hash = None
                        tq.status = u'PENDING'
                        tq.update()

                    continue

            except KeyError:
                log.msg(
                    'The torrent hasnt started downloading on client just '
                    'yet. Well check again later. {}'.format(tq.torrent_hash)
                )
                continue
            except Exception as error:
                log.err(
                    'Unhandled error with torrent {}: {}'
                    .format(tq.torrent_hash, error)
                )
                [log.err(line) for line in
                    traceback.format_exc().splitlines()]
                return

            if self.app.debug:
                log.msg(
                    'ID: {} >>>>> Torrent Status: {}. Database status {} <<<<<'
                    .format(tq.torrent_queue_id, torrent.status, tq.status)
                )

            if torrent.status == 'downloading' and tq.status == 'FOUND':

                log.msg(
                    'Updating torrent ID {} status to DOWNLOADING: {}'
                    .format(tq.torrent_queue_id, tq.torrent_hash)
                )

                tq.status = u'DOWNLOADING'
                tq.update()

            elif torrent.status in ('seeding', 'stopped') \
                    and tq.status == 'DOWNLOADING':

                log.msg(
                    'Removing torrent {}. Updating status to FINISHED: {}'
                    .format(tq.torrent_queue_id, tq.torrent_hash)
                )

                self.transmission.remove_torrent_from_client(tq.torrent_hash)

                tq.status = u'FINISHED'
                tq.update()

    def __file_created(self, filename, file_id):
        log.msg('Saved file for torrent_queue_id: {}'.format(file_id))
        log.msg('Torrent saved at: {}'.format(filename))

        TorrentQueue.update_status(
            new_status=u'FOUND', torrent_queue_id=file_id, async=False
        )

    def __error_finding_torrents(self, file_name, file_id):
        log.msg(
            'Problem with downloading torrent {}, going to set '
            'to NOT_FOUND and try again later'.format(file_name)
        )

        TorrentQueue.update_status(
            new_status=u'FOUND', torrent_queue_id=file_id, async=False
        )

    def _create_directory(self, torrent_queue_id):
        """ Create a directory for content of files downloaded """

        movie = Movie.find(
            Movie.torrent_queue_id == torrent_queue_id, async=False
        ).one()
        if movie is not None:
            return self.__mkdir(movie.name)

        tv_show = TVShow.find(
            TVShow.torrent_queue_id == torrent_queue_id, async=False
        ).one()
        if tv_show is not None:
            return self.__mkdir(tv_show.name)

        return None

    def __mkdir(self, name):
        """ Creates the directory if not exists """

        directory = os.path.join(self.app.torrent_destination, name)

        if not os.path.exists(directory):
            os.makedirs(directory)

        return directory


class TransmissionWrapper(object):
    """ Small wrapper class for the Transmission Client library
        TODO: See if we can make these functions async
    """

    def __init__(self, app):
        super(TransmissionWrapper, self).__init__()

        try:
            self.client = transmissionrpc.Client(
                app.transmission_client['host'],
                port=app.transmission_client['port']
            )
            self.is_active = True
        except transmissionrpc.TransmissionError as e:
            log.msg('Error: {}'.format(e))
            self.is_active = False

    @check_connection
    def remove_torrent_from_client(self, torrent_id, stop=False):
        """ Removes torrent from client """

        if not self.is_active:
            return

        if stop:
            self.stop_torrent(torrent_id)

        return self.client.remove_torrent(torrent_id)

    @check_connection
    def get_torrent(self, torrent_id):
        """ Returns a single torrent object """

        if not self.is_active:
            return

        return self.client.get_torrent(torrent_id)

    @check_connection
    def get_torrents(self, torrent_ids=None):
        """ Returns list of torrent objects
            :param: list containing torrent_ids
        """

        if not self.is_active:
            return

        if not torrent_ids:
            return self.client.get_torrents()

        if len(torrent_ids) > 0:
            torrents = ':'.join(torrent_ids)
        elif len(torrent_ids) == 0:
            torrents = str(torrent_ids[0])
        else:
            torrents = None

        if torrents:
            return self.client.get_torrents(torrents)

        return None

    @check_connection
    def add_torrent(self, url, directory=None):
        """ Adds torrent to queue """

        if not self.is_active:
            return

        return self.client.add_torrent(url, download_dir=directory)

    def _ping(self):
        """ Using the get session stats as a way to ping client """

        return self.client.session_stats()
