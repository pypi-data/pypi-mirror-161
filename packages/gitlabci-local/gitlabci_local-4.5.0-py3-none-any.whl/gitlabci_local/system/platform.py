#!/usr/bin/env python3

# Standard libraries
from os import access, environ, R_OK, sep
from os.path import expanduser
from pathlib import Path, PurePosixPath
from sys import platform, stdin, stdout

# Platform
class Platform:

    # Environment
    ENV_ANDROID = 'ANDROID_ROOT'
    ENV_EXPERIMENTAL = 'EXPERIMENTAL'
    ENV_SIMULATE_MAC_OS = 'SIMULATE_MAC_OS'
    ENV_SUDO_USER = 'SUDO_USER'

    # Constants
    IS_ANDROID = ('ANDROID_ROOT' in environ)
    IS_EXPERIMENTAL = (ENV_EXPERIMENTAL in environ)
    IS_LINUX = (platform in ['linux', 'linux2'])
    IS_MAC_OS = (platform in ['darwin'] or ENV_SIMULATE_MAC_OS in environ)
    IS_SIMULATED = (ENV_SIMULATE_MAC_OS in environ)
    IS_WINDOWS = (platform in ['win32', 'win64'])

    # Paths
    BUILDS_DIR = PurePosixPath('/builds')

    # Separators
    PATH_SEPARATOR = sep

    # TTYs
    IS_TTY_STDIN = stdin.isatty() and stdin.encoding != 'cp1252'
    IS_TTY_STDOUT = stdout.isatty()
    IS_TTY_UTF8 = str(stdout.encoding).lower() == 'utf-8'

    # Users
    IS_USER_SUDO = (ENV_SUDO_USER in environ)
    USER_SUDO = environ[ENV_SUDO_USER] if IS_USER_SUDO else ''

    # Flush
    @staticmethod
    def flush():
        print('', end='', flush=Platform.IS_TTY_STDOUT)

    # Userspace
    @staticmethod
    def userspace(name):

        # Variables
        home = None

        # Elevated home
        if Platform.IS_USER_SUDO:
            home = Path(expanduser(f'~{Platform.USER_SUDO}'))
            if not access(home, R_OK):
                home = None

        # Default home
        if not home or not home.is_dir():
            home = Path.home()

        # Windows userspace
        if Platform.IS_WINDOWS:
            return home / 'AppData' / 'Local' / name

        # macOS userspace
        if Platform.IS_MAC_OS:
            return home / 'Library' / 'Preferences' / name

        # Linux userspace
        return home / '.config' / name
