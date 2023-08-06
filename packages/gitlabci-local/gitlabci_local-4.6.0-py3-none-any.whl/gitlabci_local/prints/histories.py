#!/usr/bin/env python3

# Standard libraries
from os import environ
from time import time

# Components
from ..package.bundle import Bundle
from ..prints.colors import Colors
from ..system.platform import Platform

# TimedHistory class, pylint: disable=too-few-public-methods
class TimedHistory:

    # Members
    __duration = 0
    __start_time = 0

    # Constructor
    def __init__(self):
        self.__duration = 0
        self.__start_time = time()

    # Refresh times
    def _refresh_times(self):

        # Acquire fake duration
        if Bundle.ENV_HISTORIES_DURATION_FAKE in environ:
            duration = int(environ[Bundle.ENV_HISTORIES_DURATION_FAKE])

        # Evaluate duration
        else:
            duration = int(time() - self.__start_time)

        # Evaluate seconds
        seconds = f"{duration % 60:.0f} second{'s' if duration % 60 > 1 else ''}"

        # Evaluate minutes
        minutes = ''
        if duration >= 60:
            minutes = f"{duration / 60:.0f} minute{'s' if duration / 60 > 1 else ''} "

        # Store total time
        self.__duration = minutes + seconds

    @property
    def duration(self):
        return self.__duration

# JobHistory class
class JobHistory(TimedHistory):

    # Constants
    __SYMBOL_FAILED = '✘' if Platform.IS_TTY_UTF8 else 'x'
    __SYMBOL_FOOTER = '‣' if Platform.IS_TTY_UTF8 else '>'
    __SYMBOL_SKIPPED = '»' if Platform.IS_TTY_UTF8 else '~'
    __SYMBOL_SUCCESS = '✔' if Platform.IS_TTY_UTF8 else 'v'
    __SYMBOL_WARNING = '!'

    # Members
    __details = ''
    __failure_allowed = False
    __name = None
    __result = None
    __stage = None

    # Constructor
    def __init__(self, name, stage):
        super().__init__()
        self.__details = ''
        self.__failure_allowed = False
        self.__name = name
        self.__result = None
        self.__stage = stage

    @property
    def failure_allowed(self):
        return self.__failure_allowed

    @failure_allowed.setter
    def failure_allowed(self, value):
        self.__failure_allowed = value

    @property
    def details(self):
        return self.__details

    @details.setter
    def details(self, value):
        self.__details = value

    @property
    def name(self):
        return self.__name

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, value):
        self.__result = value
        self._refresh_times()

    # Header
    def header(self, jobs_count, image, engine_type):

        # Header output
        if jobs_count > 1:
            print(' ')
        print(
            f' {Colors.GREEN}===[ {Colors.YELLOW}{self.__stage}:' \
                f' {Colors.YELLOW}{self.__name} {Colors.CYAN}' \
                    f'({image}, {engine_type}) {Colors.GREEN}]==={Colors.RESET}'
        )
        print(' ')
        Platform.flush()

    # Footer
    def footer(self):

        # Footer output
        print(f'  {Colors.YELLOW}{self.__SYMBOL_FOOTER} {self.__name}:' \
                f' {Colors.GREEN if self.result else Colors.RED}' \
                    f"{'Success' if self.result else 'Failure'}" \
                    f' in {self.duration}{Colors.CYAN}{self.details}{Colors.RESET}')
        print(' ')
        Platform.flush()

    # Print
    def print(self):

        # Variables
        icon = ''
        summary = ''

        # Print result
        if self.result:
            icon = f'{Colors.GREEN}{self.__SYMBOL_SUCCESS}'
            summary = f'{Colors.GREEN}Success in {self.duration}'
        elif self.failure_allowed:
            icon = f'{Colors.YELLOW}{self.__SYMBOL_WARNING}'
            summary = f'{Colors.YELLOW}Failure in {self.duration}'
        elif self.result is None:
            icon = f'{Colors.GREY}{self.__SYMBOL_SKIPPED}'
            summary = f'{Colors.GREY}Skipped'
        else:
            icon = f'{Colors.RED}{self.__SYMBOL_FAILED}'
            summary = f'{Colors.RED}Failure in {self.duration}'

        # Print result
        print(
            f'    {icon} {Colors.BOLD}{self.name}:' \
                f' {summary}{Colors.CYAN}{self.details}{Colors.RESET}'
        )

# StageHistory class
class StageHistory:

    # Constants
    __SYMBOL_STAGE = '•' if Platform.IS_TTY_UTF8 else '-'

    # Members
    __jobs = []
    __name = None

    # Constructor
    def __init__(self, name):
        self.__jobs = []
        self.__name = name

    @property
    def name(self):
        return self.__name

    # Add
    def add(self, job_name):

        # Add job
        job = JobHistory(job_name, self.name)
        self.__jobs += [job]

        # Result
        return job

    # Print
    def print(self):

        # Stage header
        print(f'  {Colors.YELLOW}{self.__SYMBOL_STAGE} Stage {self.name}:{Colors.RESET}')

        # Iterate through jobs
        for job in self.__jobs:
            job.print()

# PipelineHistory class
class PipelineHistory(TimedHistory):

    # Constants
    __SYMBOL_PIPELINE = '‣' if Platform.IS_TTY_UTF8 else '>'

    # Members
    __jobs_count = 0
    __jobs_quiet = True
    __pipeline = None
    __result = None

    # Constructor
    def __init__(self):
        super().__init__()
        self.__jobs_count = 0
        self.__jobs_quiet = True
        self.__pipeline = []
        self.__result = None

    @property
    def jobs_count(self):
        return self.__jobs_count

    @property
    def jobs_quiet(self):
        return self.__jobs_quiet

    @jobs_quiet.setter
    def jobs_quiet(self, value):
        self.__jobs_quiet = value

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, value):
        self.__result = value
        self._refresh_times()

    # Add
    def add(self, stage_name, job_name):

        # Increment jobs count
        self.__jobs_count += 1

        # Find stage
        stage = self.get(stage_name)

        # Prepare stage
        if not stage:
            stage = StageHistory(stage_name)
            self.__pipeline += [stage]

        # Add job
        job = stage.add(job_name)

        # Result
        return job

    # Get
    def get(self, stage_name):

        # Find stage
        for stage in self.__pipeline:
            if stage.name == stage_name:
                return stage

        # Fallback
        return None

    # Print
    def print(self):

        # Header
        print(' ')
        print(
            f' {Colors.GREEN}===[ {Colors.YELLOW}Pipeline:' \
                f' {Colors.BOLD}{self.jobs_count} jobs {Colors.GREEN}]==={Colors.RESET}'
        )
        print(' ')

        # Iterate through stages
        for stage in self.__pipeline:
            stage.print()
            print(' ')

        # Footer
        print(
            f'  {Colors.YELLOW}{self.__SYMBOL_PIPELINE} Pipeline:' \
                f' {Colors.BOLD if self.result else Colors.RED}' \
                    f"{'Success' if self.result else 'Failure'}" \
                        f' in {self.duration} total{Colors.RESET}'
        )
        print(' ')
