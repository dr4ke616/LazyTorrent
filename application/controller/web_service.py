# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2014 - adamdrakeford@gmail.com

"""
.. controller:: WebService
    :platform: Linux
    :synopsis: RESTful API interface controller for Auto Torrent

.. controllerauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import json
import urllib
import traceback

from twisted.python import log
from mamba.web.response import Ok, InternalServerError
from mamba.application import route
from mamba.application import controller

from application.model.tv_show import TVShow
from application.model.movie import Movie
from application.model.torrent_queue import TorrentQueue


class WebService(controller.Controller):
    """
    RESTful API interface controller for Auto Torrent
    """

    name = 'WebService'
    __route__ = 'api'

    def __init__(self):
        """
        Put your initialization code here
        """
        super(WebService, self).__init__()

    @route('/')
    def root(self, request, **kwargs):
        return Ok('I am the WebService, hello world!')

    @route('/add/movie', method='POST')
    def add_movie(self, request, **kwargs):
        """ Creates a new movie and adds it to the torrent queue
            JSON Data in the form of:
            [
                {
                    "title": string,
                    "dvd_release": date object,
                    "theater_release": date object,
                    "rating": string,
                    "download_now": boolean
                },
                {
                    ...
                }
            ]
        """

        ## TODO: This needs to be sent over application/json
        # header request. Some reason it wouldnt work for me.
        data = kwargs.get('data')
        data = urllib.unquote(data).decode('utf8')
        log.msg('JSON: {}'.format(data))

        try:
            data = json.loads(data)
        except ValueError:
            log.err('Problem with your JSON string')
            data = {}

        ## Check we have all arguments we need
        for m in data:
            check = self._check_args(m, ('title'))
            if check is not None:
                return Ok(check)

        count = 0
        for movie in data:
            download_now = movie.pop('download_now', True)
            movie['name'] = movie.pop('title')

            try:
                count += 1
                Movie(**movie).create(download_now=download_now)
            except Exception as e:
                msg = 'Error adding Movie {}'.format(movie['name'])
                log.err('{}: {}'.format(msg, e))
                [log.err(line) for line in
                    traceback.format_exc().splitlines()]
                return InternalServerError(
                    self._generate_response(code=500, message=msg))

        return Ok(self._generate_response(
            code=0,
            message='Added {}/{} Movies to queue'.format(count, len(data)))
        )

    @route('/add/tv_show', method='POST')
    def add_tv_show(self, request, **kwargs):
        """Creates a new movie and adds it to the torrent queue
            JSON Data in the form of:
            [
                {
                    "title": string,
                    "season_number": int,
                    "episode_number": int,
                    "air_date": date object,
                    "episode_name": string,
                    "rating": string,
                    "download_now": boolean
                },
                {
                    ...
                }
            ]
        """

        ## TODO: This needs to be sent over application/json
        # header request. Some reason it wouldnt work for me.
        data = kwargs.get('data')
        data = urllib.unquote(data).decode('utf8')
        log.msg('JSON: {}'.format(data))

        try:
            data = json.loads(data)
        except ValueError:
            log.err('Problem with your JSON string')
            data = {}

        ## Check we have all arguments we need
        for m in data:
            check = self._check_args(
                m, ('title', 'season_number', 'episode_number')
            )
            if check is not None:
                return Ok(check)

        count = 0
        for tv_show in data:
            download_now = tv_show.pop('download_now', True)
            tv_show['name'] = tv_show.pop('title')

            try:
                count += 1
                TVShow(**tv_show).create(download_now=download_now)
            except Exception as e:
                msg = 'Error adding TVShow {}'.format(tv_show['name'])
                log.err('{}: {}'.format(msg, e))
                [log.err(line) for line in
                    traceback.format_exc().splitlines()]
                return InternalServerError(
                    self._generate_response(code=500, message=msg))

        return Ok(self._generate_response(
            code=0,
            message='Added {}/{} TV shows to queue'.format(count, len(data)))
        )

    @route('/get/queue', method=['POST', 'GET'])
    def get_torrent_queue(self, request, **kwargs):
        """Loads and returns the existing torrent queue
        """

        results = TorrentQueue.load()
        data = []
        for result in results:
            data.append({
                'torrent_queue_id': result.torrent_queue_id,
                'media_type': result.media_type,
                'query': result.query,
                'download_now': bool(result.download_now),
                'status': result.status,
                'date_added': str(result.date_added)
            })

        return Ok(self._generate_response(
            code=0,
            message='Queue',
            data=data))

    def _generate_response(self, code, message, data=None):
        resp = {
            'code': code,
            'message': message,
            'data': data
        }
        return json.dumps(resp)

    def _check_args(self, local, req_args):
        for k, v in local.iteritems():
            if k in req_args and v is None:
                return self._generate_response(
                    code=1,
                    message='{} argument required'.format(k)
                )
