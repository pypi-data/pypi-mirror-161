#!/usr/bin/env python3

# Standard libraries
from os import environ
from subprocess import DEVNULL, PIPE, Popen, run

# Components
from ..package.bundle import Bundle
from ..system.platform import Platform
from ..types.volumes import Volumes
from .interface import Interface

# Podman class
class Podman(Interface):

    # Members
    __binary = 'podman'
    __container = None

    # Constructor
    def __init__(self):

        # Prepare container
        self.__container = None

        # Configure binary
        if Bundle.ENV_PODMAN_BINARY_PATH in environ:
            self.__binary = environ[Bundle.ENV_PODMAN_BINARY_PATH]

        # Check engine support
        try:
            result = self.__exec(['system', 'info'], True)
            if result.returncode != 0:
                raise ModuleNotFoundError()
        except FileNotFoundError:
            raise ModuleNotFoundError() from None

    # Internal execution
    def __exec(self, arguments, quiet=False):

        # Execute quiet command
        if quiet:
            return run([self.__binary] + arguments, check=False, stdout=DEVNULL,
                       stderr=DEVNULL)

        # Execute standard command
        return run([self.__binary] + arguments, check=False, stdout=PIPE, stderr=PIPE)

    # Internal watcher
    def __watch(self, arguments):

        # Watch command outputs, pylint: disable=consider-using-with
        return iter(Popen([self.__binary] + arguments, stdout=PIPE).stdout.readline, b'')

    # Command exec
    def cmd_exec(self):

        # Result
        if Platform.IS_USER_SUDO:
            return f'sudo {self.__binary} exec -it'
        return f'{self.__binary} exec -it'

    # Container
    @property
    def container(self):

        # Result
        result = self.__exec(
            ['inspect', '--type', 'container', '--format', '{{.Name}}', self.__container])
        return result.stdout.strip().decode('utf-8') if result.returncode == 0 else ''

    # Exec
    def exec(self, command):

        # Adapt command
        if isinstance(command, str): # pragma: no cover
            command = [command]

        # Execute command in container
        return self.__exec(['exec', self.__container] + command)

    # Get
    def get(self, image):

        # Validate image exists
        result = self.__exec([
            'inspect',
            '--type',
            'image',
            '--format',
            'exists',
            image,
        ], True)

        # Pull missing image
        if result.returncode != 0:
            self.pull(image)

    # Logs
    def logs(self):

        # Return logs stream
        return self.__watch(['logs', '--follow', self.__container])

    # Pull
    def pull(self, image, force=False):

        # Header
        print(f'Pulling from {image}')
        Platform.flush()

        # Force image removal
        if force:
            self.rmi(image)

        # Pull image with logs stream
        result = self.__exec(['pull', image])

        # Layer completion logs
        if result.returncode == 0:
            result = self.__exec([
                'inspect',
                '--type',
                'image',
                '--format',
                '{{.Id}}',
                image,
            ])
            print(f"Digest: {result.stdout.strip().decode('utf-8')}")
            print(f'Status: Image is up to date for {image}')
        else:
            print(f'Status: Image not found for {image}')
            Platform.flush()
            raise FileNotFoundError(result.stderr.decode('utf-8').replace('\\n', '\n'))

        # Footer
        print(' ')
        Platform.flush()

    # Remove
    def remove(self):

        # Remove container
        if self.__container:
            self.__exec(['rm', '--force', self.__container])
            self.__container = None

    # Remove image
    def rmi(self, image):

        # Remove image
        result = self.__exec([
            'inspect',
            '--type',
            'image',
            '--format',
            'exists',
            image,
        ], True)
        if result.returncode == 0:
            self.__exec([
                'rmi',
                image,
            ])

    # Run, pylint: disable=too-many-arguments,too-many-locals,unused-argument
    def run(self, image, command, entrypoint, variables, network, option_sockets,
            services, volumes, directory, temp_folder):

        # Variables
        args_command = []
        args_entrypoint = []
        args_env = []
        args_run = []
        args_volumes = []

        # Adapt command
        if isinstance(command, list): # pragma: no cover
            args_command = command
        elif isinstance(command, str):
            args_command = [command]

        # Adapt entrypoint
        if isinstance(entrypoint, list):
            if len(entrypoint) > 1:
                args_command = [' '.join(args_command)]
                args_command[0:0] = entrypoint[1:]
            entrypoint = entrypoint[0]
        if isinstance(entrypoint, str):
            args_entrypoint = ['--entrypoint', entrypoint]

        # Adapt mounts
        if volumes and isinstance(volumes.get(), dict):
            for volume in volumes.get().items():
                args_volumes += ['--volume', f'{Volumes.stringify(volume)}']

        # Adapt variables
        for variable in variables:
            args_env.extend(['--env', f'{variable}={variables[variable]}'])

        # Prepare arguments
        args_run += ['create']
        args_run += args_entrypoint
        args_run += args_env
        args_run += ['--tty']
        args_run += args_volumes
        if network:
            args_run += ['--network', network]
        args_run += ['--privileged']
        args_run += ['--security-opt', 'label=disable']
        args_run += ['--workdir', directory]
        args_run += [image]
        args_run += args_command

        # Create container image
        result = self.__exec(args_run)
        if result.returncode == 0:
            self.__container = result.stdout.strip().decode('utf-8')

        # Handle creation failures
        else:
            raise NotImplementedError(result.stderr.decode('utf-8').replace('\\n', '\n'))

        # Start container
        result = self.__exec(['start', self.__container])

        # Handle start failures
        if result.returncode != 0: # pragma: no cover
            raise RuntimeError(result.stderr.decode('utf-8').replace('\\n', '\n'))

    # Stop
    def stop(self, timeout):

        # Stop container
        self.__exec(['stop', '--time', str(timeout), self.__container])

    # Supports
    def supports(self, binary):

        # Validate binary support
        result = self.exec(['whereis', binary])

        # Result
        return result.returncode == 0

    # Wait
    def wait(self):

        # Wait container
        result = self.__exec(['wait', self.__container])

        # Result
        return int(result.stdout.strip()) == 0 if result.returncode == 0 else False
