#!/usr/bin/env python3

# Components
from ..prints.colors import Colors
from ..system.platform import Platform

# Outputs class
class Outputs:

    # Debugging
    @staticmethod
    def debugging(container_exec, container_name, shell):

        # Debugging informations
        print(' ')
        print(
            f'  {Colors.YELLOW}‣ INFORMATION: {Colors.BOLD}' \
                f"Use '{Colors.CYAN}{container_exec} {container_name} {shell}" \
                f'{Colors.BOLD}\' commands for debugging. Interrupt with Ctrl+C...{Colors.RESET}'
        )
        print(' ')
        Platform.flush()

    # Interruption
    @staticmethod
    def interruption():

        # Interruption output
        print(' ')
        print(' ')
        print(
            f'  {Colors.YELLOW}‣ WARNING: {Colors.BOLD}' \
                f'User interruption detected, stopping the container...{Colors.RESET}'
        )
        print(' ')
        Platform.flush()

    # Warning
    @staticmethod
    def warning(message): # pragma: no cover

        # Warning output
        print(f'  {Colors.YELLOW}‣ WARNING: {Colors.BOLD}{message}{Colors.RESET}')
        print(' ')
        Platform.flush()
