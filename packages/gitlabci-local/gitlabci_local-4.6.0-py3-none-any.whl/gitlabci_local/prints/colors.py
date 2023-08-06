#!/usr/bin/env python3

# Modules libraries
from colored import attr, fg

# Colors class, pylint: disable=too-few-public-methods
class Colors:

    # Constants
    BOLD = attr('reset') + attr('bold')
    CYAN = fg('cyan') + attr('bold')
    GREEN = fg('green') + attr('bold')
    GREY = fg('light_gray') + attr('bold')
    RED = fg('red') + attr('bold')
    RESET = attr('reset')
    YELLOW = fg('yellow') + attr('bold')
    YELLOW_LIGHT = fg('light_yellow') + attr('bold')

    # Attributes
    ALL = [BOLD, CYAN, GREEN, GREY, RED, RESET, YELLOW, YELLOW_LIGHT]
