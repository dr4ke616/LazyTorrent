# -*- coding: utf-8 -*-
"""
.. module:: Downloader
    :synopsis: Used to download remote files

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""


from twisted.python import log

from web_client import WebClient


class _Queue(object):
    workers = 0
    tasks = []

    def __init__(self, host, use_tor, concurrency=0):
        self.host = host
        self.concurrency = concurrency
        self.queue_empty = None
        self.on_file_created = None
        self.errback = None
        self.use_tor = use_tor

    def push(self, data):
        self.tasks.append({
            'data': data,
            'client': WebClient(self.host, self.use_tor)
        })

        if len(self.tasks) == self.concurrency:
            log.err('Queue is saturated')
            return
        self.process()

    def _process_error(self, failure, file_name, file_id):
        log.err(str(failure))
        log.err(failure.getTraceback())

        if self.errback is not None:
            self.errback(file_name, file_id)

    def _process_data(self, response, file_name, file_id):
        if response is None:
            log.err('No response when downloading file.')
            if self.errback is not None:
                self.errback()
            return

        with open(file_name, 'w') as f:
            f.write(response)
        f.close()

        if self.on_file_created:
            self.on_file_created(file_name, file_id)

        self.workers -= 1
        self.process()

    def process(self):
        if self.workers >= self.concurrency:
            log.err('Too many workers')
            return

        if len(self.tasks) == 0:
            if self.queue_empty:
                self.queue_empty()
            log.msg('Queue now empty')
            return

        task = self.tasks.pop(0)
        self.workers += 1

        client = task['client']
        path = task['data']['remote_file']
        file_name = task['data']['location']
        file_id = task['data']['id']

        d = client.request_page(path)
        d.addCallback(self._process_data, file_name, file_id)
        d.addErrback(self._process_error, file_name, file_id)


class Downloader(object):
    def __init__(self, host, use_tor):
        """
        The path_to_file variable can set so that if downloading
        multiple files from the same location, you can specify a url
        (with no host). Meaning that only the file names are needed
        in the dictionaries being passed into the get method
        """
        self.queue = _Queue(host, use_tor, 100)
        self.path_to_file = None

    def get(self, files_to_download, **kwargs):
        """
        Adds files to download queue.
        :param files_to_download: tuple
            Tupple can contain one or more dict.
            The dictionary items must have two keys,
            one for the name of the remote file
            and the other for the name (and directory)
            of the file to be downloaded. Example:
            {
                'remote_file': 'download/file.txt',
                'location': '/tmp/files/file.txt',
                'id': X
            }
        :param queue_empty: callback when queue is empty
        :param on_file_created: callback when file is created.
            Path to file passed as paramater
        :param errback: callback executed when something goes wrong
        """
        if type(files_to_download) is not tuple:
            raise ValueError('Expected Tupple containing lists')

        # self.queue.concurrency = len(files_to_download) + 1

        if 'queue_empty' in kwargs:
            self.queue.queue_empty = kwargs['queue_empty']
            del kwargs['queue_empty']

        if 'on_file_created' in kwargs:
            self.queue.on_file_created = kwargs['on_file_created']
            del kwargs['on_file_created']

        if 'errback' in kwargs:
            self.queue.errback = kwargs['errback']
            del kwargs['errback']

        for f in files_to_download:
            if 'remote_file' not in f.keys() or 'location' not in f.keys():
                raise ValueError(
                    'remote_file and location need to be specified'
                )

            if self.path_to_file is not None:
                f['remote_file'] = self.path_to_file + f['remote_file']

            self.queue.push(f)
