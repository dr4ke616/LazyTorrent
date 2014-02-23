# -*- encoding: utf-8 -*-
# -*- mamba-file-type: mamba-model -*-

"""
.. model:: BaseModel
    :platform: Unix Windows
    :synopsis: BaseModel model

.. modelauthor:: Adam Drakeford <adam.drakeford@gmail.com>
"""


class ModelError(Exception):
    """Base exception class for model errors
    """


def required(obj, attr, value):
    if value is None:
        raise ModelError('{0}: required value'.format(attr))

    return value
