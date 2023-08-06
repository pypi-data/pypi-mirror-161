#!/usr/bin/env python3

# Modules libraries
try:
    from PyInquirer import style_from_dict as PyInquirer_style_from_dict
    from PyInquirer import Token as PyInquirer_Token
    PYINQUIRER_AVAILABLE = True
except ImportError: # pragma: no cover
    PYINQUIRER_AVAILABLE = False

# Menus class, pylint: disable=too-few-public-methods
class Menus:

    # Themes class, pylint: disable=too-few-public-methods
    class Themes:

        # Constants
        CYAN = '#00FFFF bold'
        GREEN = '#00FF00 bold'
        YELLOW = '#FFFF00 bold'

        # PyInquirer features
        if PYINQUIRER_AVAILABLE:

            # Selector theme
            SELECTOR = PyInquirer_style_from_dict({
                PyInquirer_Token.Separator: YELLOW,
                PyInquirer_Token.QuestionMark: YELLOW,
                PyInquirer_Token.Selected: GREEN,
                PyInquirer_Token.Instruction: CYAN,
                PyInquirer_Token.Pointer: YELLOW,
                PyInquirer_Token.Answer: CYAN,
                PyInquirer_Token.Question: GREEN,
            })

            # Configurations theme
            CONFIGURATIONS = PyInquirer_style_from_dict({
                PyInquirer_Token.Selected: GREEN,
                PyInquirer_Token.Instruction: CYAN,
                PyInquirer_Token.Pointer: YELLOW,
                PyInquirer_Token.Answer: CYAN,
                PyInquirer_Token.Question: YELLOW,
            })
