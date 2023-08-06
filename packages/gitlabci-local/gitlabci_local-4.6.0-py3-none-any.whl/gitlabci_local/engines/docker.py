#!/usr/bin/env python3

# Standard libraries
from os import environ

# Modules libraries
from docker import from_env
from docker.errors import APIError, DockerException, ImageNotFound

# Components
from ..jobs.outputs import Outputs
from ..system.platform import Platform
from .interface import Interface

# Docker class
class Docker(Interface):

    # Constants
    ENV_DOCKER_CERT_PATH = 'DOCKER_CERT_PATH'
    ENV_DOCKER_HOST = 'DOCKER_HOST'
    ENV_DOCKER_TLS_VERIFY = 'DOCKER_TLS_VERIFY'

    # Members
    __client = None
    __container = None

    # Constructor
    def __init__(self):

        # Prepare container
        self.__container = None

        # Engine client
        try:
            self.__client = from_env()
            self.__client.ping()
        except DockerException:
            raise ModuleNotFoundError() from None

    # Sockets, pylint: disable=no-self-use
    def __sockets(self, variables, volumes):

        # Variables
        docker_host = ''

        # Detect TLS configurations
        if Docker.ENV_DOCKER_TLS_VERIFY in environ:
            variables[Docker.ENV_DOCKER_TLS_VERIFY] = environ[
                Docker.ENV_DOCKER_TLS_VERIFY]

        # Detect certificates configurations
        if Docker.ENV_DOCKER_CERT_PATH in environ:
            variables[Docker.ENV_DOCKER_CERT_PATH] = '/certs'
            volumes.add(environ[Docker.ENV_DOCKER_CERT_PATH], '/certs', 'ro', True)

        # Detect host configurations
        if Docker.ENV_DOCKER_HOST in environ and environ[Docker.ENV_DOCKER_HOST]:
            docker_host = environ[Docker.ENV_DOCKER_HOST]

        # Network Docker socket
        if docker_host[0:7] == 'http://' or docker_host[0:6] == 'tcp://':
            variables[Docker.ENV_DOCKER_HOST] = docker_host

        # Local Docker socket
        elif docker_host[0:7] == 'unix://': # pragma: no cover
            volumes.add(docker_host[7:], docker_host[7:], 'rw', True)

        # Default Docker socket
        elif not docker_host: # pragma: no cover

            # Add socket volume
            if Platform.IS_LINUX or Platform.IS_WINDOWS or Platform.IS_EXPERIMENTAL:
                volumes.add('/var/run/docker.sock', '/var/run/docker.sock', 'rw', True)

            # Unavailable feature
            else:
                Outputs.warning('The Docker sockets feature is not available...')

        # Unknown feature
        else: # pragma: no cover
            Outputs.warning(
                f'The {Docker.ENV_DOCKER_HOST} = {docker_host}' \
                    ' configuration is not supported yet...'
            )

    # Command exec, pylint: disable=no-self-use
    def cmd_exec(self):

        # Result
        return 'docker exec -it'

    # Container
    @property
    def container(self):

        # Result
        return self.__container.name

    # Exec
    def exec(self, command):

        # Execute command in container
        return self.__container.exec_run(command)

    # Get
    def get(self, image):

        # Validate image exists
        try:
            self.__client.images.get(image)

        # Pull missing image
        except ImageNotFound:
            self.pull(image)

    # Logs
    def logs(self):

        # Return logs stream
        return self.__container.logs(stream=True)

    # Pull
    def pull(self, image, force=False):

        # Force image removal
        if force:
            self.rmi(image)

        # Pull image with logs stream
        for data in self.__client.api.pull(image, stream=True, decode=True):

            # Layer progress logs
            if 'progress' in data:
                if Platform.IS_TTY_STDOUT:
                    print(f"\r\x1b[K{data['id']}: {data['status']} {data['progress']}",
                          end='')
                    Platform.flush()

            # Layer event logs
            elif 'progressDetail' in data:
                if Platform.IS_TTY_STDOUT:
                    print(f"\r\x1b[K{data['id']}: {data['status']}", end='')
                    Platform.flush()

            # Layer completion logs
            elif 'id' in data:
                print(f"\r\x1b[K{data['id']}: {data['status']}")
                Platform.flush()

            # Image logs
            else:
                print(f"\r\x1b[K{data['status']}")
                Platform.flush()

        # Footer
        print(' ')
        Platform.flush()

    # Remove
    def remove(self):

        # Remove container
        if self.__container:
            self.__container.remove(force=True)
            self.__container = None

    # Remove image
    def rmi(self, image):

        # Remove image
        try:
            self.__client.api.remove_image(image)
        except ImageNotFound:
            pass

    # Run, pylint: disable=too-many-arguments,unused-argument
    def run(self, image, command, entrypoint, variables, network, option_sockets,
            services, volumes, directory, temp_folder):

        # Append sockets mounts
        if option_sockets:
            self.__sockets(variables, volumes)

        # Run container image
        self.__container = self.__client.containers.run(
            image=image,
            command=command,
            detach=True,
            entrypoint=entrypoint,
            environment=variables,
            network_mode=network if network else 'bridge',
            privileged=True,
            remove=False,
            stdout=True,
            stderr=True,
            stream=True,
            volumes=volumes.get(),
            working_dir=directory,
        )

    # Stop
    def stop(self, timeout):

        # Stop container
        self.__container.stop(timeout=timeout)

    # Supports
    def supports(self, binary):

        # Variables
        exit_code = 1

        # Validate binary support
        try:
            exit_code, unused_output = self.exec(f'whereis {binary}')
        except APIError: # pragma: no cover
            pass

        # Result
        return exit_code == 0

    # Wait
    def wait(self):

        # Wait container
        result = self.__container.wait()

        # Result
        return result['StatusCode'] == 0
