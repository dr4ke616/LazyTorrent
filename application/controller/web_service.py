# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-controller -*-
# Copyright (c) 2014 - adamdrakeford@gmail.com

"""
.. controller:: WebService
    :platform: Linux
    :synopsis: Web Service for form based front end

.. controllerauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from mamba.web.response import Ok
from mamba.application import route
from mamba.application import controller


class WebService(controller.Controller):
    """
    RESTful API interface controller for Auto Torrent
    """

    name = 'WebService'
    __route__ = 'web'

    def __init__(self):
        """
        Put your initialization code here
        """
        super(WebService, self).__init__()

    @route('/')
    def root(self, request, **kwargs):
        return Ok('I am the WebService, hello world!')
