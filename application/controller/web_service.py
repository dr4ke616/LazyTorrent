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

    @route('/add/movie', method=['POST', 'GET'])
    def add_movie(self, request, **kwargs):
        """Creates a new movie and adds it to the torrent queue
        """

        title = kwargs.get('title')
        dvd_release = kwargs.get('dvd_release', None)
        theater_release = kwargs.get('theater_release', None)
        rating = kwargs.get('rating', None)
        download_now = kwargs.get('download_now', True)

        check = self._check_args(locals(), ('title'))
        if check is not None:
            return Ok(check)

        if type(download_now) == str:
            download_now = True if download_now.lower() == 'true' else False

        ## TODO:
        # Convert any date types to date objects
        # Cast any other appropiate variables

        try:
            Movie(
                name=title,
                dvd_release=dvd_release,
                theater_release=theater_release,
                rating=rating).create(download_now=download_now)
        except Exception as e:
            msg = 'There was an error adding Movie {}'.format(title)
            log.err('{}: {}'.format(msg, e))
            [log.err(line) for line in
                traceback.format_exc().splitlines()]
            return InternalServerError(
                self._generate_response(code=500, message=msg))

        return Ok(self._generate_response(
            code=0, message='{} added to queue'.format(title)))

    @route('/add/tv_show', method=['POST', 'GET'])
    def add_tv_show(self, request, **kwargs):
        """Creates a new movie and adds it to the torrent queue
        """

        title = kwargs.get('title')
        season_number = kwargs.get('season')
        episode_number = kwargs.get('episode')
        air_date = kwargs.get('air_date', None)
        episode_name = kwargs.get('episode_name', None)
        rating = kwargs.get('rating', None)
        download_now = kwargs.get('download_now', True)

        check = self._check_args(
            locals(), ('title', 'season_number', 'episode_number')
        )
        if check is not None:
            return Ok(check)

        if type(download_now) == str:
            download_now = True if download_now.lower() == 'true' else False

        ## TODO:
        # Convert any date types to date objects
        # Cast any other appropiate variables

        try:
            TVShow(
                name=title,
                season_number=int(season_number),
                episode_number=int(episode_number),
                air_date=air_date,
                episode_name=episode_name,
                rating=rating).create(download_now=download_now)
        except Exception as e:
            msg = 'There was an error adding TVShow {}'.format(title)
            log.err('{}: {}'.format(msg, e))
            [log.err(line) for line in
                traceback.format_exc().splitlines()]
            return InternalServerError(
                self._generate_response(code=500, message=msg))

        return Ok(self._generate_response(
            code=0, message='{} added to queue'.format(title)))

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
