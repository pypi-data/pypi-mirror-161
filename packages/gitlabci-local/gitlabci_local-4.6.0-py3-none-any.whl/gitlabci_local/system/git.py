#!/usr/bin/env python3

# Standard libraries
from os import environ
from subprocess import CalledProcessError, check_output, DEVNULL

# Components
from ..package.bundle import Bundle

# Git class
class Git:

    # Members
    __binary: str = 'git'

    # Constructor
    def __init__(self):

        # Configure binary
        if Bundle.ENV_GIT_BINARY_PATH in environ:
            self.__binary = environ[Bundle.ENV_GIT_BINARY_PATH]

    # HEAD revision hash
    def head_revision_hash(self, workdir=None):

        # Result
        try:
            return check_output(
                [self.__binary, 'rev-parse', 'HEAD'],
                cwd=workdir,
                shell=False,
                stderr=DEVNULL,
            ).strip().decode()
        except (CalledProcessError, FileNotFoundError):
            return ''

    # HEAD revision short hash
    def head_revision_short_hash(self, workdir=None):

        # Result
        try:
            return check_output(
                [self.__binary, 'rev-parse', '--short', 'HEAD'],
                cwd=workdir,
                shell=False,
                stderr=DEVNULL,
            ).strip().decode()
        except (CalledProcessError, FileNotFoundError):
            return ''
