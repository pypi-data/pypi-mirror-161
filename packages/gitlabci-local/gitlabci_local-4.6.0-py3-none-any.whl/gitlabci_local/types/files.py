#!/usr/bin/env python3

# Standard libraries
from atexit import register, unregister
from os import getpid, kill
from pathlib import Path
from signal import getsignal, SIGINT, signal, SIGTERM
from tempfile import NamedTemporaryFile

# Files class
class Files:

    # Members
    registered = False
    signal_int = None
    signal_term = None
    temps = []

    # Register
    @staticmethod
    def __register():

        # Register cleanup
        if not Files.registered:
            register(Files.clean)
            Files.signal_int = getsignal(SIGINT)
            Files.signal_term = getsignal(SIGTERM)
            signal(SIGINT, Files.clean)
            signal(SIGTERM, Files.clean)
            Files.registered = True

    # Unregister
    @staticmethod
    def __unregister():

        # Unregister cleanup
        if Files.registered:
            unregister(Files.clean)
            signal(SIGINT, Files.signal_int)
            signal(SIGTERM, Files.signal_term)
            Files.registered = False

    # Clean
    @staticmethod
    def clean(signo=None, unused_frame=None):

        # Delete all temps
        for temp in Files.temps:
            temp_file = Path(temp.name)
            if temp_file.exists():
                temp_file.unlink()

        # Reset temps
        Files.temps = []

        # Unregister signals
        Files.__unregister()

        # Raise signal
        if signo:
            kill(getpid(), signo)

    # Temp
    @staticmethod
    def temp(path=None, mode='wt', newline='\n', prefix='.tmp.'):

        # Create temporary file, pylint: disable=consider-using-with
        temp_file = NamedTemporaryFile(delete=False, dir=path, mode=mode, newline=newline,
                                       prefix=prefix)

        # Register temporary file
        Files.temps += [temp_file]

        # Register signals
        Files.__register()

        # Result
        return temp_file
