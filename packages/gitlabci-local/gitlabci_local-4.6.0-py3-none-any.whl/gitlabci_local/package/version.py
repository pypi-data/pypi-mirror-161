#!/usr/bin/env python3

# Standard libraries
from os import environ
from sys import version_info

# Modules libraries
from pkg_resources import DistributionNotFound, require

# Components
from ..system.platform import Platform
from .bundle import Bundle

# Version class
class Version:

    # Getter
    @staticmethod
    def get():

        # Fake test version
        if Bundle.ENV_VERSION_FAKE in environ:
            return environ[Bundle.ENV_VERSION_FAKE]

        # Acquire version
        try:
            name = __name__.split('.', maxsplit=1)[0]
            return require(name)[0].version

        # Default fallback
        except DistributionNotFound: # pragma: no cover
            return '0.0.0'

    # Path
    @staticmethod
    def path():

        # Acquire path
        path = __file__

        # Strip package path
        index = path.rfind(Platform.PATH_SEPARATOR)
        index = path.rfind(Platform.PATH_SEPARATOR, 0, index)
        path = path[0:index]

        # Result
        return path

    # Python
    @staticmethod
    def python():

        # Acquire Python version
        version = f'{version_info.major}.{version_info.minor}'

        # Result
        return version
