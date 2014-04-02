#!/usr/bin/env python
"""
.. script:: transmission_controller
    :synopsis: Starts up and shuts down transmission programmily

.. moduleauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

import os
import subprocess

from mamba.utils import config


def start():
    # p = subprocess.Popen(['ps' 'aux' '|' 'grep' '[t]ransmission-gtk'])

    p = subprocess.Popen(['transmission-gtk'])

    output, error = p.communicate()

    if error is not '':
        raise RuntimeError(error)

    print p.pid


def main():
    start()


if __name__ == '__main__':
    main()
