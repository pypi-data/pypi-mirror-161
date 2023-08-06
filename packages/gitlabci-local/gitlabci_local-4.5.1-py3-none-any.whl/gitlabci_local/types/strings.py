#!/usr/bin/env python3

# Standard libraries
from random import choices
from string import ascii_letters, digits

# Components
from ..prints.colors import Colors

# Strings class
class Strings:

    # Center
    @staticmethod
    def center(string, length):

        # Extract text
        text = Strings.strip(string)

        # Center string
        if len(text) < length:
            paddings = length - len(text)
            left = paddings // 2
            right = -(-paddings // 2)
            return ' ' * left + string + ' ' * right

        # Default string
        return string

    # Quote
    @staticmethod
    def quote(string): # pragma: no cover

        # Single quotes
        if '\'' not in string:
            return '\'' + string + '\''

        # Double quotes
        if '\"' not in string:
            return '\"' + string + '\"'

        # Adaptive quotes
        return '\'' + string.replace('\'', '\\\'') + '\''

    # Random
    @staticmethod
    def random(length): # pragma: no cover

        # Generate random string
        return ''.join(choices(ascii_letters + digits, k=length))

    # Strip
    @staticmethod
    def strip(string):
        for item in Colors.ALL:
            string = string.replace(item, '')
        return string

    # Wrap
    @staticmethod
    def wrap(string, length):

        # Variables
        color = ''
        index = 0
        line_data = ''
        line_length = 0
        lines = []
        space = ''
        word = ''

        # Length limitations
        length = max(length, 1)

        # Append line
        def append_line():
            nonlocal line_data, line_length, lines
            if line_length > 0:
                lines += [line_data]
                line_data = ''
                line_length = 0

        # Store word
        def store_word():
            nonlocal color, length, line_data, line_length, space, word
            if len(word) > 0:

                # Word overflows
                if line_length + len(space) + len(word) > length:
                    word_full = word
                    if len(word_full) > length:
                        while len(word_full) > 0:
                            word = word_full[0:length]
                            store_word()
                            word_full = word_full[length:]
                    append_line()

                # Word spacing
                if line_length > 0 and space:
                    line_data += space
                    line_length += len(space)
                space = ''

                # Word appendation
                line_data += color + word
                line_length += len(word)
                word = ''

                # Line wrapping
                if line_length >= length:
                    append_line()

        # Add char
        def add_char(char):
            nonlocal index, word
            index += 1
            word += char

        # Iterate through chars
        while index < len(string):

            # Space separator
            if string[index] == ' ':

                # Store last word
                store_word()

                # Reset word data
                space += ' '
                index += 1
                continue

            # Color marker
            for item in Colors.ALL:
                if item and string[index:].startswith(item):

                    # Store last word
                    store_word()

                    # Store new color
                    color = item
                    index += len(color)
                    break

            # Text content
            else:

                # Append character
                add_char(string[index])

        # Store last word
        store_word()

        # Append last line
        append_line()

        # Result
        return lines
