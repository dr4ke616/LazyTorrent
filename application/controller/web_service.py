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
from dateutil import parser

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
                    "dvd_release": date object,     (optional)
                    "theater_release": date object, (optional)
                    "rating": string,               (optional)
                    "download_when": date object    (optional)
                },
                {
                    ...
                }
            ]
        """

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

        for movie in data:
            error = self._create_movie(movie)

            if error is not None:
                return InternalServerError(
                    self._generate_response(code=500, message=error))

        return Ok(self._generate_response(
            code=0,
            message='Added {} Movies to queue'.format(len(data)))
        )

    def _create_movie(self, movie):
        """ Creates a movie entry in DB.
            :param movie: dict containing movie data
        """

        name = movie.get('title')
        dvd_release = movie.get('dvd_release')
        theater_release = movie.get('theater_release')
        rating = movie.get('rating')
        download_when = movie.get('download_when')

        if dvd_release is not None:
            dvd_release = parser.parse(dvd_release)

        if theater_release is not None:
            theater_release = parser.parse(theater_release)

        if download_when is not None:
            download_when = parser.parse(download_when)

        args = {
            'name': name,
            'dvd_release': dvd_release,
            'theater_release': theater_release,
            'rating': rating
        }

        try:
            Movie(**args).create(download_when=download_when)
        except Exception as e:
            msg = 'Error adding Movie {}'.format(movie['name'])
            log.err('{}: {}'.format(msg, e))
            [log.err(line) for line in
                traceback.format_exc().splitlines()]
            return msg

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
            air_date = tv_show.get('air_date')

            if air_date is not None:
                tv_show['air_date'] = parser.parse(air_date)

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
            message='Added {} out of {} TV shows to queue'.format(
                count, len(data))
            )
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
