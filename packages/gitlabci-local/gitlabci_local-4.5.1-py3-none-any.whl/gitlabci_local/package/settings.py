#!/usr/bin/env python3

# Standard libraries
from configparser import ConfigParser
from sys import stdout

# Components
from ..prints.colors import Colors
from ..system.platform import Platform

# Settings class
class Settings:

    # Constants
    SETTINGS_FILE = 'settings.ini'

    # Members
    __folder = None
    __path = None
    __settings = None

    # Constructor
    def __init__(self, name):

        # Prepare paths
        self.__folder = Platform.userspace(name)
        self.__path = self.__folder / Settings.SETTINGS_FILE

        # Parse settings
        self.__settings = ConfigParser()
        self.__settings.read(self.__path)

        # Prepare missing settings
        try:
            if self.get('package', 'name') != name:
                raise ValueError('Missing settings files')
        except ValueError:
            self.__prepare()
            self.__reset(name)

    # Prepare
    def __prepare(self):

        # Prepare folder path
        if not Platform.IS_SIMULATED:
            self.__folder.mkdir(parents=True, exist_ok=True)

    # Reset
    def __reset(self, name):

        # Prepare barebone settings
        self.__settings = ConfigParser()
        self.set('package', 'name', name)

    # Writer
    def __write(self):

        # Write initial settings
        if not Platform.IS_SIMULATED:
            with open(self.__path, encoding='utf8', mode='w') as output:
                self.__settings.write(output)

    # Get
    def get(self, group, key):

        # Get settings key in group
        if group in self.__settings and key in self.__settings[group]:
            return self.__settings[group][key]

        # Default fallback
        return None

    # Set
    def set(self, group, key, value):

        # Prepare group
        if group not in self.__settings:
            self.__settings[group] = {}

        # Set key
        self.__settings[group][key] = str(value)

        # Write updated settings
        self.__write()

    # Show
    def show(self):

        # Settings file path
        print(' ')
        print(
            f' {Colors.GREEN}===[ {Colors.YELLOW}Settings:' \
                f' {Colors.BOLD}{self.__path} {Colors.GREEN}]==={Colors.RESET}'
        )
        print(' ')

        # Settings simulated contents
        if Platform.IS_SIMULATED:
            self.__settings.write(stdout)

        # Settings file contents
        else:
            with open(self.__path, encoding='utf8', mode='r') as data:
                print(data.read())
            Platform.flush()
