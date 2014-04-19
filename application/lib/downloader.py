# -*- coding: utf-8 -*-
"""
.. module:: Downloader
    :synopsis: Used to download remote files

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""


from twisted.python import log
from twisted.web.client import readBody

from application.lib import webclient


class Downloader(object):
    tasks = []

    def __init__(self, use_tor=False):
        self.use_tor = use_tor

        # Callbacks
        self.queue_empty = None
        self.on_file_created = None
        self.errback = None

    def get(self, files_to_download, **kwargs):
        """
        Adds files to download queue.
        :param files_to_download: tuple
            Tupple or list can contain one or more dict.
            The dictionary items must have two keys,
            one for the name of the remote file
            and the other for the name (and directory)
            of the file to be downloaded. A third argument can
            be provided for the ID of the file. Example:
            {
                'url': 'http://host/download/file.txt',
                'location': '/tmp/files/file.txt',
                'id': X
            }
        :param queue_empty: callback when queue is empty
        :param on_file_created: callback when file is created.
            Path to file passed as paramater
        :param errback: callback executed when something goes wrong
        """
        if type(files_to_download) not in (tuple, list):
            raise ValueError('Expected Tupple or List')

        if 'queue_empty' in kwargs:
            self.queue_empty = kwargs['queue_empty']
            del kwargs['queue_empty']

        if 'on_file_created' in kwargs:
            self.on_file_created = kwargs['on_file_created']
            del kwargs['on_file_created']

        if 'errback' in kwargs:
            self.errback = kwargs['errback']
            del kwargs['errback']

        for f in files_to_download:
            if 'url' not in f.keys() or 'download_location' not in f.keys():
                raise ValueError(
                    'url and download_location need to be specified'
                )

            self.push(f)

    def push(self, data):
        self.tasks.append(data)
        self.process()

    def _process_error(self, failure, file_location, file_id):
        log.err(str(failure))
        log.err(failure.getTraceback())

        if self.errback is not None:
            self.errback(file_location, file_id)

    def _process_data(self, response, file_location, file_id):
        if response is None:
            log.err('No response when downloading file.')
            if self.errback is not None:
                self.errback()
            return

        with open(file_location, 'w') as f:
            f.write(response)
        f.close()

        if self.on_file_created:
            self.on_file_created(file_location, file_id)

        self.process()

    def _process_response(self, response, file_location, file_id):
        log.msg('Response Code: {}'.format(response.code))

        d = readBody(response)
        d.addCallback(self._process_data, file_location, file_id)
        d.addErrback(self._process_error, file_location, file_id)
        return d

    def process(self):
        if len(self.tasks) == 0:
            if self.queue_empty:
                self.queue_empty()
            log.msg('Queue now empty')
            return

        task = self.tasks.pop(0)

        url = task['url']
        file_location = task['download_location']
        file_id = task.get('id')

        defer = webclient.get(url, '', use_tor=self.use_tor)
        defer.addCallback(self._process_response, file_location, file_id)
        defer.addErrback(self._process_error, file_location, file_id)
