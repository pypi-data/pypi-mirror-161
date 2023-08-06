#!/usr/bin/env python3

# Modules libraries
from prompt_toolkit.styles.style import Style as prompt_toolkit_styles_Style

# Themes class, pylint: disable=too-few-public-methods
class Themes:

    # Constants
    BOLD = 'bold'
    CYAN = '#00FFFF bold'
    DISABLED = 'italic'
    GREEN = '#00FF00 bold noreverse'
    SELECTED = 'bold noreverse'
    YELLOW = '#FFFF00 bold'

    # Checkbox theme
    CHECKBOX = prompt_toolkit_styles_Style([
        ('answer', CYAN),
        ('disabled', DISABLED),
        ('instruction', CYAN),
        ('highlighted', BOLD),
        ('pointer', YELLOW),
        ('qmark', YELLOW),
        ('question', GREEN),
        ('selected', SELECTED),
        ('separator', YELLOW),
    ])

    # Configurations theme
    CONFIGURATIONS = prompt_toolkit_styles_Style([
        ('answer', CYAN),
        ('instruction', CYAN),
        ('highlighted', GREEN),
        ('pointer', YELLOW),
        ('qmark', YELLOW),
        ('question', YELLOW),
        ('selected', SELECTED),
        ('separator', YELLOW),
    ])

    # Graphics theme
    POINTER = '»'
