#!/usr/bin/env python3

# Modules libraries
try:
    from PyInquirer import Separator as PyInquirer_Separator
    from PyInquirer.prompts import list as PyInquirer_prompts_list
    from PyInquirer.prompts.common import if_mousedown as PyInquirer_if_mousedown
    from PyInquirer.prompts.list import basestring as PyInquirer_basestring
    from prompt_toolkit.layout.controls import TokenListControl as prompt_toolkit_TokenListControl
    from prompt_toolkit.token import Token as prompt_toolkit_Token
    PYINQUIRER_AVAILABLE = True
except ImportError: # pragma: no cover
    PYINQUIRER_AVAILABLE = False

# pylint: skip-file

# PyInquirer features
if PYINQUIRER_AVAILABLE:

    # Override with https://github.com/CITGuru/PyInquirer/pull/88
    class InquirerControl(prompt_toolkit_TokenListControl):
        def __init__(self, choices, **kwargs):
            self.selected_option_index = 0
            self.answered = False
            self.choices = choices
            self._init_choices(choices)
            super(InquirerControl, self).__init__(self._get_choice_tokens, **kwargs)

        def _init_choices(self, choices, default=None):
            # helper to convert from question format to internal format
            self.choices = [] # list (name, value, disabled)
            searching_first_choice = True
            for i, c in enumerate(choices):
                if isinstance(c, PyInquirer_Separator):
                    self.choices.append((c, None, None))
                else:
                    if isinstance(c, PyInquirer_basestring):
                        self.choices.append((c, c, None))
                    else:
                        name = c.get('name')
                        value = c.get('value', name)
                        disabled = c.get('disabled', None)
                        self.choices.append((name, value, disabled))
                    if searching_first_choice:
                        self.selected_option_index = i # found the first choice
                        searching_first_choice = False

        @property
        def choice_count(self):
            return len(self.choices)

        def _get_choice_tokens(self, cli):
            tokens = []
            T = prompt_toolkit_Token

            def append(index, choice):
                selected = (index == self.selected_option_index)

                @PyInquirer_if_mousedown
                def select_item(cli, mouse_event): # pragma: no cover
                    # bind option with this index to mouse event
                    self.selected_option_index = index
                    self.answered = True
                    cli.set_return_value(None)

                if isinstance(choice[0], PyInquirer_Separator):
                    tokens.append((T.PyInquirer_Separator, f'  {choice[0]}\n'))
                else:
                    tokens.append(
                        (T.Pointer if selected else T, ' \u276f ' if selected else '   '))
                    if selected:
                        tokens.append((prompt_toolkit_Token.SetCursorPosition, ''))
                    if choice[2]: # disabled
                        tokens.append((T.Selected if selected else T,
                                       f'- {choice[0]} ({choice[2]})'))
                    else:
                        try:
                            tokens.append((T.Selected if selected else T, str(
                                choice[0]), select_item))
                        except: # pragma: no cover
                            tokens.append(
                                (T.Selected if selected else T, choice[0], select_item))
                    tokens.append((T, '\n'))

            # prepare the select choices
            for i, choice in enumerate(self.choices):
                append(i, choice)
            tokens.pop() # Remove last newline.
            return tokens

        def get_selection(self):
            return self.choices[self.selected_option_index]

# Patcher class
class Patcher:

    # Constructor
    def __init__(self):

        # PyInquirer features
        if PYINQUIRER_AVAILABLE:

            # Apply library patches
            PyInquirer_prompts_list.InquirerControl = InquirerControl
