#!/usr/bin/env python3

# Standard libraries
from json import load as json_load
from os import environ
from pathlib import Path

# Modules libraries
from oyaml import safe_load as yaml_safe_load
try:
    from PyInquirer import prompt as PyInquirer_prompt
    from PyInquirer import Separator as PyInquirer_Separator
    PYINQUIRER_AVAILABLE = True
except ImportError: # pragma: no cover
    PYINQUIRER_AVAILABLE = False

# Components
from ..package.bundle import Bundle
from ..package.patcher import Patcher
from ..prints.colors import Colors
from ..prints.menus import Menus
from ..system.platform import Platform
from ..types.dicts import Dicts
from ..types.lists import Lists
from .pipelines import PipelinesFeature

# MenusFeature class
class MenusFeature:

    # Members
    __jobs = None
    __options = None

    # Constructor
    def __init__(self, jobs=None, options=None):

        # Prepare jobs
        self.__jobs = jobs

        # Prepare options
        self.__options = options

        # Patch theme
        Patcher()

    # Select, pylint: disable=too-many-branches,too-many-statements
    def select(self):

        # Variables
        default_check = self.__options.all
        jobs_available = False
        jobs_choices = []
        result = True
        stage = ''

        # Stages groups
        for job in self.__jobs:

            # Filter names
            if self.__options.names:

                # Filter jobs list
                if not self.__options.pipeline and not Lists.match(
                        self.__options.names, job, ignore_case=self.__options.ignore_case,
                        no_regex=self.__options.no_regex):
                    continue

                # Filter stages list
                if self.__options.pipeline and not Lists.match(
                        self.__options.names, self.__jobs[job]['stage'],
                        ignore_case=self.__options.ignore_case,
                        no_regex=self.__options.no_regex):
                    continue

            # Stages separator
            if stage != self.__jobs[job]['stage']:
                stage = self.__jobs[job]['stage']

                # PyInquirer missing
                if not PYINQUIRER_AVAILABLE: # pragma: no cover
                    jobs_choices += [f'\n Stage {stage}:']

                # PyInquirer features
                else:
                    jobs_choices += [PyInquirer_Separator(f'\n Stage {stage}:')]

            # Initial job details
            job_details = ''
            job_details_list = []

            # Disabled jobs
            disabled = False
            if self.__jobs[job]['when'] in ['manual'] and not self.__options.manual:
                disabled = 'Manual'
            else:
                if self.__jobs[job]['when'] == 'manual':
                    job_details_list += ['Manual']
                elif self.__jobs[job]['when'] == 'on_failure':
                    job_details_list += ['On failure']
                jobs_available = True

            # Parser disabled jobs
            if self.__jobs[job]['options']['disabled']:
                disabled = self.__jobs[job]['options']['disabled']

            # Failure allowed jobs
            if self.__jobs[job]['allow_failure']:
                job_details_list += ['Failure allowed']

            # Register job tags
            tags = ''
            if self.__jobs[job]['tags']:
                tags = f" [{','.join(self.__jobs[job]['tags'])}]"

            # Prepare job details
            if job_details_list:
                job_details = f" ({', '.join(job_details_list)})"

            # Job choices
            jobs_choices += [{
                'name': f"{self.__jobs[job]['name']}{tags}{job_details}",
                'value': job,
                'checked': default_check,
                'disabled': disabled
            }]

        # Prepare jobs selection
        selection_type = 'list' if self.__options.list else 'checkbox'
        selection_prompt = [{
            'type': selection_type,
            'qmark': '',
            'message': '===[ Jobs selector ]===',
            'name': 'jobs',
            'choices': jobs_choices
        }]

        # PyInquirer missing
        if not PYINQUIRER_AVAILABLE: # pragma: no cover
            print(f' {Colors.GREEN}===[ Jobs list ]==={Colors.RESET}')
            for jobs_choice in jobs_choices:
                if 'name' in jobs_choice:
                    print(f'  {Colors.BOLD}-{Colors.RESET} {jobs_choice["name"]}')
                else:
                    print(f' {Colors.YELLOW}{jobs_choice}{Colors.RESET}')
            answers = None

        # Request jobs selection
        elif jobs_choices and jobs_available:
            answers = PyInquirer_prompt(selection_prompt, style=Menus.Themes.SELECTOR)

        # No jobs found
        else:
            print(
                f' {Colors.GREEN}{Bundle.NAME}: {Colors.RED}ERROR:' \
                    f' {Colors.BOLD}No jobs found for selection{Colors.RESET}'
            )
            answers = None

        # Parse jobs selection
        if answers and 'jobs' in answers:
            if self.__options.list:
                self.__options.names = [answers['jobs']]
            else:
                self.__options.names = answers['jobs']
        else:
            self.__options.names = []

        # Drop pipeline mode for jobs
        self.__options.pipeline = False

        # Footer
        print(' ')
        print(' ')
        Platform.flush()

        # Launch jobs
        if self.__options.names:
            result = PipelinesFeature(self.__jobs, self.__options).launch()

        # Result
        return result

    # Configure, pylint: disable=too-many-branches,too-many-locals,too-many-statements
    def configure(self, configurations):

        # Variables
        result = {}

        # Header
        print(' ')
        print(
            f' {Colors.GREEN}===[ {Colors.YELLOW}Configurations menu' \
                f' {Colors.GREEN}]==={Colors.RESET}'
        )
        print(' ')
        Platform.flush()

        # Walk through configurations
        for variable in configurations:

            # Variables
            variable_choices = []
            variable_default = ''
            variable_index = 0
            variable_set = False
            variable_values = []

            # Extract configuration fields
            variable_node = configurations[variable]
            variable_help = variable_node['help']
            variable_type = variable_node['type']

            # Prepare configuration selection
            configuration_prompt = [{
                'name': variable,
                'qmark': '',
                'message': f'Variable {variable}: {variable_help}:',
            }]

            # Extract environment variable
            if variable in environ:
                variable_default = environ[variable]
                variable_set = True

            # Parse configuration types: boolean
            if variable_type == 'boolean':
                if 'default' in variable_node and variable_node['default'] in [
                        False, 'false'
                ]:
                    variable_values = ['false', 'true']
                else:
                    variable_values = ['true', 'false']
                if not variable_set:
                    variable_default = variable_values[0]
                for choice in variable_values:
                    variable_index += 1
                    variable_choices += [{
                        # 'key': str(variable_index),
                        'name': f'{choice}',
                        'value': choice
                    }]
                configuration_prompt[0]['type'] = 'list'
                configuration_prompt[0]['choices'] = variable_choices

            # Parse configuration types: choice
            elif variable_type == 'choice':
                variable_values = variable_node['values']
                if not variable_set:
                    variable_default = variable_values[0]
                for choice in variable_values:
                    variable_index += 1
                    variable_choices += [{
                        'key': str(variable_index),
                        'name': f'{choice}',
                        'value': choice
                    }]
                configuration_prompt[0]['type'] = 'list'
                configuration_prompt[0]['choices'] = variable_choices

            # Parse configuration types: input
            elif variable_type == 'input':
                configuration_prompt[0]['type'] = 'input'
                if 'default' in variable_node and variable_node[
                        'default'] and not variable_set:
                    variable_default = variable_node['default']
                    configuration_prompt[0]['default'] = variable_default

            # Parse configuration types: json
            elif variable_type == 'json':
                if not variable_set:
                    configuration_path = Path(self.__options.path) / variable_node['path']
                    configuration_key = variable_node['key']
                    with open(configuration_path, encoding='utf8',
                              mode='r') as configuration_data:
                        configuration_dict = json_load(configuration_data)
                        variable_values = Dicts.find(configuration_dict,
                                                     configuration_key)
                        if not variable_values:
                            raise ValueError(
                                f'Unknown "{configuration_key}" key in' \
                                    f' {configuration_path} for f"{variable}"'
                            )
                        if isinstance(variable_values, str):
                            variable_values = [variable_values]
                        for choice in variable_values:
                            variable_index += 1
                            variable_choices += [{
                                'key': str(variable_index),
                                'name': f'{choice}',
                                'value': choice
                            }]
                        configuration_prompt[0]['type'] = 'list'
                        configuration_prompt[0]['choices'] = variable_values
                        variable_default = variable_values[0]

            # Parse configuration types: yaml
            elif variable_type == 'yaml':
                if not variable_set:
                    configuration_path = Path(self.__options.path) / variable_node['path']
                    configuration_key = variable_node['key']
                    with open(configuration_path, encoding='utf8',
                              mode='r') as configuration_data:
                        configuration_dict = yaml_safe_load(configuration_data)
                        variable_values = Dicts.find(configuration_dict,
                                                     configuration_key)
                        if not variable_values:
                            raise ValueError(
                                f'Unknown "{configuration_key}" key in' \
                                    f' {configuration_path} for f"{variable}"'
                            )
                        if isinstance(variable_values, str):
                            variable_values = [variable_values]
                        for choice in variable_values:
                            variable_index += 1
                            variable_choices += [{
                                'key': str(variable_index),
                                'name': f'{choice}',
                                'value': choice
                            }]
                        configuration_prompt[0]['type'] = 'list'
                        configuration_prompt[0]['choices'] = variable_values
                        variable_default = variable_values[0]

            # Parse configuration types: unknown
            else:
                print(' ')
                print(
                    f' {Colors.GREEN}{Bundle.NAME}: {Colors.RED}ERROR:' \
                        f' {Colors.BOLD}Unsupported configuration type ' \
                            f'"{variable_type}"...{Colors.RESET}'
                )
                print(' ')
                Platform.flush()
                raise NotImplementedError(
                    f'Unsupported configuration type "{variable_type}"')

            # Extract environment variable
            if variable in environ:
                variable_default = environ[variable]
                variable_set = True

            # Request configuration selection
            if not Platform.IS_TTY_STDIN or variable_set or self.__options.defaults \
                    or not PYINQUIRER_AVAILABLE:
                result[variable] = str(variable_default)
                print(
                    f" {Colors.YELLOW}{configuration_prompt[0]['message']}" \
                        f'  {Colors.CYAN}{result[variable]}{Colors.RESET}'
                )
            else:
                answers = PyInquirer_prompt(configuration_prompt,
                                            style=Menus.Themes.CONFIGURATIONS)
                if not answers:
                    raise KeyboardInterrupt
                result[variable] = str(answers[variable])

        # Footer
        print(' ')
        Platform.flush()

        # Result
        return result
