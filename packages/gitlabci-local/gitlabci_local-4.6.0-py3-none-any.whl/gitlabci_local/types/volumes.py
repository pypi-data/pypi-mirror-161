#!/usr/bin/env python3

# Components
from ..system.platform import Platform
from ..types.paths import Paths

# Volumes class
class Volumes:

    # Constants
    LOCAL_FLAG = '.local:'

    # Members
    __volumes = None

    # Constructor
    def __init__(self):
        self.__volumes = {}

    # Add
    def add(self, source, target, mode, override):

        # Handle overrides
        if target in [volume['bind'] for _, volume in self.__volumes.items()]:
            if not override:
                return

            # Detect duplicated volumes
            duplicates = [
                key for key, volume in self.__volumes.items()
                if volume['.source'] == source and volume['bind'] == target
            ]
            if duplicates:
                self.__volumes.pop(duplicates[0])

        # Adapt source to allow duplicates
        while source in self.__volumes:
            if Platform.IS_WINDOWS: # pragma: no cover
                source = f'{source}{Platform.PATH_SEPARATOR}.'
            else:
                source = f'{Platform.PATH_SEPARATOR}.{source}'

        # Add volume binding
        self.__volumes[source] = { #
            'bind': target,
            'mode': mode,
            '.source': source
        }

    # Get
    def get(self):
        return self.__volumes

    # Parse
    @staticmethod
    def parse(volume):

        # Invalid volume
        if not volume:
            raise ValueError('Empty volume parameter cannot be parsed')

        # Relative volume
        if 1 <= len(volume) <= 2:
            return [volume]

        # Variables
        volume_node = ''
        volume_nodes = []

        # Iterate through volume
        for char in f'{volume}\x00':

            # Detect Windows drive
            if char == ':' and len(volume_node) == 1 and volume_node[0].isalpha():
                volume_node += char # pragma: no cover

            # Detect separator or end
            elif char in (':', ';', '\0'):
                volume_nodes += [Paths.translate(volume_node)]
                volume_node = ''

            # Append to volume node
            else:
                volume_node += char

        # Result
        return volume_nodes

    # Stringify
    @staticmethod
    def stringify(volume):

        # Variables
        options = ''

        # Extract options
        if volume[1]['mode'] == 'ro':
            options += ':ro'
        elif volume[1]['mode'] == 'rw':
            options += ':rw'

        # Result
        return f"{volume[0]}:{volume[1]['bind']}{options}"
