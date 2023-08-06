#!/usr/bin/env python3

# Standard libraries
from enum import Enum

# Components
from .docker import Docker
from .podman import Podman

# Backend enumeration
class Backend(Enum):
    DOCKER = 1
    PODMAN = 2
    UNKNOWN = 3

# Names enumeration, pylint: disable=too-few-public-methods
class Names:

    # Constants
    AUTO = 'auto'
    DOCKER = 'docker'
    PODMAN = 'podman'

    # Defaults
    DEFAULTS = [
        PODMAN,
        DOCKER,
    ]

    # Getter
    @staticmethod
    def get(override):

        # Adapt override
        override = override.lower() if override else None

        # Handle engine overrides
        if override:
            auto = False
            names = []
            overrides = override.split(',')
            for item in overrides:
                if item:
                    if Names.AUTO == item:
                        auto = True
                    else:
                        names += [name for name in Names.DEFAULTS if name == item]
            if auto or override[-1] == ',':
                names = names + Names.DEFAULTS
            names = list(dict.fromkeys(names))

        # Use engine defaults
        else:
            names = Names.DEFAULTS

        # Result
        return names

# Supported engines
def supported():
    return [Names.AUTO] + Names.DEFAULTS

# Engine class
class Engine:

    # Members
    __engine = None
    __name = None

    # Constructor
    def __init__(self, options):

        # Acquire engine names
        names = Names.get(options.engine)

        # Iterate through names
        for name in names:

            # Detect Docker engine
            if name == Names.DOCKER:
                try:
                    self.__engine = Docker()
                    self.__name = Names.DOCKER
                    break
                except (KeyboardInterrupt, ModuleNotFoundError):
                    self.__engine = None

            # Detect Podman engine
            elif name == Names.PODMAN:
                try:
                    self.__engine = Podman()
                    self.__name = Names.PODMAN
                    break
                except (KeyboardInterrupt, ModuleNotFoundError):
                    self.__engine = None

        # Unknown engine fallback
        if not self.__engine:
            raise NotImplementedError('Unknown or unsupported container engine...')

    # Command exec
    def cmd_exec(self):
        return self.__engine.cmd_exec()

    # Container
    @property
    def container(self):
        return self.__engine.container

    # Exec
    def exec(self, command): # pragma: no cover
        return self.__engine.exec(command)

    # Get
    def get(self, image):
        self.__engine.get(image)

    # Logs
    def logs(self):
        return self.__engine.logs()

    # Name
    @property
    def name(self):
        return self.__name

    # Pull
    def pull(self, image, force=False):
        self.__engine.pull(image, force=force)

    # Remove
    def remove(self):
        self.__engine.remove()

    # Remove image
    def rmi(self, image):
        self.__engine.rmi(image)

    # Run, pylint: disable=too-many-arguments
    def run(self, image, command, entrypoint, variables, network, option_sockets,
            services, volumes, directory, temp_folder):
        return self.__engine.run(
            image=image,
            command=command,
            entrypoint=entrypoint,
            variables=variables,
            network=network,
            option_sockets=option_sockets,
            services=services,
            volumes=volumes,
            directory=directory,
            temp_folder=temp_folder,
        )

    # Stop
    def stop(self, timeout):
        self.__engine.stop(timeout)

    # Supports
    def supports(self, binary):
        return self.__engine.supports(binary)

    # Wait
    def wait(self):
        return self.__engine.wait()
