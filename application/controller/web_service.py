# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: WebService
    :platform: Unix Windows
    :synopsis: RESTful Web Service controller

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""

import traceback

from twisted.python import log
from twisted.internet import defer, task, reactor

from mamba import Mamba
from mamba.utils import config
from mamba.application import route
from mamba.application import controller
from mamba.web.response import Ok, BadRequest, Created

from application.model.tv_show import TVShow
from application.model.movie import Movie


class WebService(controller.Controller):
    """
    REST WebService for Auto Torrnet
    """

    name = 'WebService'
    __route__ = 'api'

    def __init__(self):
        """
        Put your initialization code here
        """
        super(WebService, self).__init__()

    @route('/', method='GET')
    def root(self, request, **kwargs):
        return Ok('You have reached my auto torrent downloader app')

    @route('/add/movie', method=['POST', 'GET'])
    def add_movie(self, request, **kwargs):
        """Creates a new movie and adds it to the torrent queue
        """
        name = request.forms.get('title')
        dvd_release = request.forms.get('dvd_release', None)
        theater_release = request.forms.get('theater_release', None)
        rating = request.forms.get('rating', None)
        download_now = request.forms.get('download_now', True)

        if name is None:
            raise ValueError('Missing args')

        Movie(
            name=name,
            dvd_release=dvd_release,
            theater_release=theater_release,
            rating=rating).create(download_now=download_now)

    @route('/add/tv_show', method=['POST', 'GET'])
    def add_tv_show(self, request, **kwargs):
        """Creates a new movie and adds it to the torrent queue
        """
        name = request.forms.get('title')
        season_number = request.forms.get('season_number')
        episode_number = request.forms.get('episode_number')
        air_date = request.forms.get('air_date', None)
        episode_name = request.forms.get('episode_name', None)
        rating = request.forms.get('rating', None)
        download_now = request.forms.get('download_now', True)

        if name is None or season_number is None or episode_number is None:
            raise ValueError('Missing args')

        TVShow(
            name=name,
            season_number=season_number,
            air_date=air_date,
            episode_name=episode_name,
            rating=rating).create(download_now=download_now)
