#!/usr/bin/env python3

# Standard libraries
from abc import ABC, abstractmethod

# Interface class
class Interface(ABC): # pragma: no cover

    # Command exec
    @abstractmethod
    def cmd_exec(self):
        pass

    # Container
    @property
    @abstractmethod
    def container(self):
        pass

    # Exec
    @abstractmethod
    def exec(self, command):
        pass

    # Get
    @abstractmethod
    def get(self, image):
        pass

    # Logs
    @abstractmethod
    def logs(self):
        pass

    # Pull
    @abstractmethod
    def pull(self, image, force=False):
        pass

    # Remove
    @abstractmethod
    def remove(self):
        pass

    # Remove image
    @abstractmethod
    def rmi(self, image):
        pass

    # Run, pylint: disable=too-many-arguments
    @abstractmethod
    def run(self, image, command, entrypoint, variables, network, option_sockets,
            services, volumes, directory, temp_folder):
        pass

    # Stop
    @abstractmethod
    def stop(self, timeout):
        pass

    # Supports
    @abstractmethod
    def supports(self, binary):
        pass

    # Wait
    @abstractmethod
    def wait(self):
        pass
