# -*- coding: utf-8 -*-

from alphalogic_api.logger import Logger
from alphalogic_api import options


VERSION_MAJOR = 0  # (System version)
VERSION_MINOR = 0  # (Tests version)
BUILD_NUMBER = 21   # (Issues version)
SNAPSHOT_NUMBER = 0

__version__ = '.'.join(map(str, (VERSION_MAJOR, VERSION_MINOR, BUILD_NUMBER))) if SNAPSHOT_NUMBER == 0 \
    else '.'.join(map(str, (VERSION_MAJOR, VERSION_MINOR, BUILD_NUMBER, 'snapshot.{}'.format(SNAPSHOT_NUMBER))))


def init():
    """
    Initialize function. Should be run before Root object created.
    :return: host, port
    """
    options.parse_arguments()
    Logger()

    return options.args.host, options.args.port
