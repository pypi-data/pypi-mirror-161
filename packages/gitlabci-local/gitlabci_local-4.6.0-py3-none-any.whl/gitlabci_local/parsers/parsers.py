#!/usr/bin/env python3

# Standard libraries
from os import environ
from pathlib import Path
from sys import exc_info

# Modules libraries
from dotenv import dotenv_values
from oyaml import safe_load as yaml_safe_load, YAMLError

# Components
from ..package.bundle import Bundle
from ..prints.colors import Colors
from .gitlab import GitLab

# Parsers class, pylint: disable=too-few-public-methods
class Parsers:

    # Members
    __options = None

    # Constructor
    def __init__(self, options):

        # Prepare options
        self.__options = options

    # Read
    def read(self):

        # Variables
        environment = {
            'default': {},
            'files': [],
            'parameters': {},
        }

        # Parse environment options
        if self.__options.env:
            for env in self.__options.env:
                env_parsed = env.split('=', 1)

                # Parse VARIABLE=value
                if len(env_parsed) == 2:
                    variable = env_parsed[0]
                    value = env_parsed[1]
                    environ[variable] = value
                    environment['parameters'][variable] = value

                # Parse ENVIRONMENT_FILE
                elif (Path(self.__options.path) / env).is_file():
                    environment['files'] += [Path(self.__options.path) / env]

                # Parse VARIABLE
                else:
                    variable = env
                    if variable in environ:
                        environment['parameters'][variable] = environ[variable]
                    else:
                        environment['parameters'][variable] = ''

        # Iterate through environment files
        environment['files'].insert(0, Path(self.__options.path) / '.env')
        for environment_file in environment['files']:
            if not environment_file.is_file():
                continue

            # Parse environment files
            environment_file_values = dotenv_values(dotenv_path=environment_file)
            for variable in environment_file_values:

                # Define default environment variable
                environment['default'][variable] = environment_file_values[variable]

        # Read GitLab CI YAML
        try:
            with open(self.__options.configuration, encoding='utf8',
                      mode='r') as configuration_data:
                data = yaml_safe_load(configuration_data)
                return GitLab(self.__options).parse(data, environment)
        except YAMLError as exc:
            print(' ')
            print(
                f' {Colors.GREEN}{Bundle.NAME}: {Colors.RED}ERROR:' \
                    f' {Colors.BOLD}{exc}{Colors.RESET}'
            )
            print(' ')
        except (FileNotFoundError, PermissionError):
            print(' ')
            print(
                f' {Colors.GREEN}{Bundle.NAME}: {Colors.RED}ERROR:' \
                    f' {Colors.BOLD}{str(exc_info()[1])}{Colors.RESET}'
            )
            print(' ')

        # Failure
        return None
