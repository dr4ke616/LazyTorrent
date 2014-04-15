# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2014 - adam <adam@localhost>

"""
.. controller:: ApiService
    :platform: Linux
    :synopsis: RESTful API interface controller for Auto Torrent

.. controllerauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import json
import urllib
import traceback
from dateutil import parser

from twisted.python import log
from twisted.internet import defer
from mamba.application import route
from mamba.application import controller
from mamba.web.response import Ok, InternalServerError

from application.model.movie import Movie
from application.model.tv_show import TVShow


class ApiService(controller.Controller):
    """
    RESTful API interface controller for Auto Torrent
    """

    name = 'ApiService'
    __route__ = 'api'

    def __init__(self):
        """
        Put your initialization code here
        """
        super(ApiService, self).__init__()

    @route('/')
    def root(self, request, **kwargs):
        return Ok('I am the ApiService, hello world!')

    @route('/add/movie', method='POST')
    def add_movie(self, request, **kwargs):
        """ Creates a new movie and adds it to the torrent queue
            JSON Data in the form of:
            [
                {
                    "title": string,
                    "dvd_release": date object,     (optional)
                    "theater_release": date object, (optional)
                    "rating": int,                  (optional)
                    "download_when": date object    (optional)
                },
                {
                    ...
                }
            ]
        """

        data = kwargs.get('data')
        if data is None:
            return Ok(self._generate_response(
                code=405, message='JSON data needs to be suplied')
            )

        data = urllib.unquote(data).decode('utf8')
        log.msg('JSON: {}'.format(data))

        try:
            data = json.loads(data)
        except:
            msg = 'Problem with your JSON string'
            log.err(msg)
            return Ok(self._generate_response(code=405, message=msg))

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

        plural = 's' if len(data) > 1 else ''
        return Ok(self._generate_response(
            code=0,
            message='Added {} Movie{} to queue'.format(len(data), plural))
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
                    "air_date": date object,        (optional)
                    "episode_name": string,         (optional)
                    "rating": int,                  (optional)
                    "download_when": date object    (optional)
                },
                {
                    ...
                }
            ]
        """

        data = kwargs.get('data')
        if data is None:
            return Ok(self._generate_response(
                code=405, message='JSON data needs to be suplied')
            )

        data = urllib.unquote(data).decode('utf8')
        log.msg('JSON: {}'.format(data))

        try:
            data = json.loads(data)
        except ValueError:
            msg = 'Problem with your JSON string'
            log.err(msg)
            return Ok(self._generate_response(code=405, message=msg))

        ## Check we have all arguments we need
        for tvs in data:
            check = self._check_args(
                tvs, ('title', 'season_number', 'episode_number')
            )
            if check is not None:
                return Ok(check)

        for tv_show in data:
            error = self._create_tv_show(tv_show)

            if error is not None:
                return InternalServerError(
                    self._generate_response(code=500, message=error))

        plural = 's' if len(data) > 1 else ''
        return Ok(self._generate_response(
            code=0,
            message='Added {} TV Show{} to queue'.format(len(data), plural))
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
            dvd_release = parser.parse(dvd_release, ignoretz=True)

        if theater_release is not None:
            theater_release = parser.parse(theater_release, ignoretz=True)

        if download_when is not None:
            download_when = parser.parse(download_when, ignoretz=True)

        args = {
            'name': name,
            'dvd_release': dvd_release,
            'theater_release': theater_release,
            'rating': rating
        }

        try:
            Movie(**args).create(download_when=download_when)
        except Exception as e:
            msg = 'Error adding Movie {}'.format(movie['title'])
            log.err('{}: {}'.format(msg, e))
            [log.err(line) for line in
                traceback.format_exc().splitlines()]
            return msg

    def _create_tv_show(self, tv_show):
        """ Creates a TV Show entry in DB.
            :param tv_show: dict containing tv show data
        """

        download_when = tv_show.get('download_when')
        if download_when is not None:
            download_when = parser.parse(download_when, ignoretz=True)

        tv_show['name'] = tv_show.pop('title')

        if 'air_date' in tv_show and tv_show['air_date'] is not None:
            tv_show['air_date'] = parser.parse(
                tv_show['air_date'], ignoretz=True
            )

        try:
            TVShow(**tv_show).create(download_when=download_when)
        except Exception as e:
            msg = 'Error adding Movie {}'.format(tv_show['name'])
            log.err('{}: {}'.format(msg, e))
            [log.err(line) for line in
                traceback.format_exc().splitlines()]
            return msg

    @route('/get/queue', method=['POST', 'GET'])
    @defer.inlineCallbacks
    def get_torrent_queue(self, request, **kwargs):
        """Loads and returns the existing torrent queue
        """

        movies = yield self.get_movies()
        tv_shows = yield self.get_tvshows()

        data = {
            'TV_SHOW': tv_shows,
            'MOVIE': movies
        }

        defer.returnValue(
            Ok(self._generate_response(
                code=0, message='Full Queue', data=data))
        )

    @route('/get/queue/movie', method=['POST', 'GET'])
    @defer.inlineCallbacks
    def get_torrent_queue_movies(self, request, **kwargs):
        """Loads and returns the existing torrent queue
        """

        movies = yield self.get_movies()

        data = {
            'MOVIE': movies
        }

        defer.returnValue(
            Ok(self._generate_response(
                code=0, message='Movies Queue', data=data))
        )

    @route('/get/queue/tv_show', method=['POST', 'GET'])
    @defer.inlineCallbacks
    def get_torrent_queue_tv_show(self, request, **kwargs):
        """Loads and returns the existing torrent queue
        """

        tv_shows = yield self.get_tvshows()

        data = {
            'TV_SHOW': tv_shows
        }

        defer.returnValue(
            Ok(self._generate_response(
                code=0, message='TV Show Queue', data=data))
        )

    @defer.inlineCallbacks
    def get_movies(self, **kwargs):
        """ Loads all entries for movies
            :param kwargs: Pass in argument for querying
            :return: defered return
        """

        movies = yield Movie.find(**kwargs)

        data = list()
        for movie in movies:
            data.append({
                'name': movie.name,
                'status': movie.torrent_queue.status,
                'movie_id': movie.movie_id,
                'date_added': unicode(movie.torrent_queue.date_added),
                'download_when': unicode(movie.torrent_queue.download_when),
                'torrent_queue_id': movie.torrent_queue.torrent_queue_id
            })

        defer.returnValue(data)

    @defer.inlineCallbacks
    def get_tvshows(self, **kwargs):
        """ Loads all entries for tv shows
            :param kwargs: Pass in argument for querying
            :return: defered return
        """

        tv_shows = yield TVShow.find(**kwargs)

        data = list()
        for tv_show in tv_shows:
            data.append({
                'name': tv_show.name,
                'status': tv_show.torrent_queue.status,
                'tv_show_id': tv_show.tv_show_id,
                'date_added': unicode(tv_show.torrent_queue.date_added),
                'episode_name': tv_show.episode_name,
                'season_number': tv_show.season_number,
                'download_when': unicode(tv_show.torrent_queue.download_when),
                'episode_number': tv_show.episode_number,
                'torrent_queue_id': tv_show.torrent_queue.torrent_queue_id
            })

        defer.returnValue(data)

    def _generate_response(self, code, message, data=None):
        """ Generates the response to be sent back to client
        """

        resp = {
            'code': code,
            'message': message,
            'data': data
        }
        return json.dumps(resp)

    def _check_args(self, local, req_args):
        """ Function to check correct arguments are recieved from client
        """

        for k, v in local.iteritems():
            if k in req_args and v is None:
                return self._generate_response(
                    code=405,
                    message='{} argument required'.format(k)
                )
