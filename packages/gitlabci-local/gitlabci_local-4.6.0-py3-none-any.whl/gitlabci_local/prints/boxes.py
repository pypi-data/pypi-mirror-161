#!/usr/bin/env python3

# Standard libraries
from shutil import get_terminal_size

# Components
from ..system.platform import Platform
from ..types.strings import Strings
from .colors import Colors

# Boxes class
class Boxes:

    # Constants
    __TOP_LEFT = '╭' if Platform.IS_TTY_UTF8 else '-'
    __TOP_LINE = '─' if Platform.IS_TTY_UTF8 else '-'
    __TOP_RIGHT = '╮' if Platform.IS_TTY_UTF8 else '-'
    __MIDDLE_LEFT = '│' if Platform.IS_TTY_UTF8 else '|'
    __MIDDLE_RIGHT = '│' if Platform.IS_TTY_UTF8 else '|'
    __BOTTOM_LEFT = '╰' if Platform.IS_TTY_UTF8 else '-'
    __BOTTOM_LINE = '─' if Platform.IS_TTY_UTF8 else '-'
    __BOTTOM_RIGHT = '╯' if Platform.IS_TTY_UTF8 else '-'
    __OFFSET_LINE = 2
    __PADDING_LINE = 2

    # Members
    __lines = None

    # Constructor
    def __init__(self):
        self.__lines = []

    # Adder
    def add(self, line):
        self.__lines += [line]

    # Printer
    def print(self):

        # Evaluate lines length
        length = max(len(Strings.strip(line)) for line in self.__lines)

        # Acquire terminal width
        columns, unused_rows = get_terminal_size()

        # Limit line length
        limit = columns - Boxes.__OFFSET_LINE - len(
            Boxes.__MIDDLE_LEFT) - 2 * Boxes.__PADDING_LINE - len(Boxes.__MIDDLE_RIGHT)
        limit = max(limit, 1)
        length = min(length, limit)

        # Header
        print(' ')

        # Print header line
        print(f"{' ' * Boxes.__OFFSET_LINE}{Colors.YELLOW}{Boxes.__TOP_LEFT}" \
            f'{Boxes.__TOP_LINE * (length + 2 * Boxes.__PADDING_LINE)}{Boxes.__TOP_RIGHT}')

        # Print content lines
        for line in self.__lines:
            for part in Strings.wrap(line, length=length):
                print(
                    f"{' ' * Boxes.__OFFSET_LINE}{Colors.YELLOW}{Boxes.__MIDDLE_LEFT}" \
                        f"{' ' * Boxes.__PADDING_LINE}{Strings.center(part, length)}" \
                            f"{' ' * Boxes.__PADDING_LINE}{Colors.YELLOW}{Boxes.__MIDDLE_RIGHT}"
                )

        # Print bottom line
        print(
            f"{' ' * Boxes.__OFFSET_LINE}{Colors.YELLOW}{Boxes.__BOTTOM_LEFT}" \
                f'{Boxes.__BOTTOM_LINE * (length + 2 * Boxes.__PADDING_LINE)}' \
                    f'{Boxes.__BOTTOM_RIGHT}{Colors.RESET}'
        )

        # Footer
        print(' ')
        Platform.flush()
