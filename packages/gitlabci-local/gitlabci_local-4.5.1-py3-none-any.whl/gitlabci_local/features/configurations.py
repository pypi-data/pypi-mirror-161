#!/usr/bin/env python3

# Standard libraries
from copy import deepcopy
from sys import maxsize

# Modules libraries
from oyaml import dump as yaml_dump

# Components
from ..system.platform import Platform
from ..types.lists import Lists

# ConfigurationsFeature class, pylint: disable=too-few-public-methods
class ConfigurationsFeature:

    # Members
    __configuration = None

    # Constructor
    def __init__(self, jobs, options):

        # Prepare configuration
        self.__configuration = {}
        if options.names:
            for job in jobs:
                if Lists.match(options.names, job, ignore_case=options.ignore_case,
                               no_regex=options.no_regex):
                    self.__configuration[job] = deepcopy(jobs[job])
                    self.__cleanup(job)
        else:
            for job in jobs:
                self.__configuration[job] = deepcopy(jobs[job])
                self.__cleanup(job)

    # Cleanup
    def __cleanup(self, job):

        # Cleanup job configurations
        if job in self.__configuration:
            if self.__configuration[job]['entrypoint'] is None:
                del self.__configuration[job]['entrypoint']
            if self.__configuration[job]['retry'] == 0:
                del self.__configuration[job]['retry']
            if not self.__configuration[job]['services']:
                del self.__configuration[job]['services']
            if self.__configuration[job]['tags'] is None:
                del self.__configuration[job]['tags']
            if self.__configuration[job]['trigger'] is None:
                del self.__configuration[job]['trigger']
            if not self.__configuration[job]['variables']:
                del self.__configuration[job]['variables']
            del self.__configuration[job]['options']

    # Dump
    def dump(self):

        # Dump configuration results
        print(yaml_dump(self.__configuration, indent=2, width=maxsize))
        print(' ')
        Platform.flush()

        # Result
        return bool(self.__configuration)
