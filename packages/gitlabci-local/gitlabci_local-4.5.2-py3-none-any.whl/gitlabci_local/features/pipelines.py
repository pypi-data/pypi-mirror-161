#!/usr/bin/env python3

# Components
from ..jobs.runner import Jobs
from ..prints.histories import PipelineHistory
from ..system.platform import Platform
from ..types.lists import Lists

# PipelinesFeature class, pylint: disable=too-few-public-methods
class PipelinesFeature:

    # Members
    __jobs = None
    __options = None

    # Constructor
    def __init__(self, jobs, options):

        # Prepare jobs
        self.__jobs = jobs

        # Prepare options
        self.__options = options

    # Filter
    def __filter(self, job):

        # Filter jobs list
        if not self.__options.pipeline and not Lists.match(
                self.__options.names, job, ignore_case=self.__options.ignore_case,
                no_regex=self.__options.no_regex):
            return False

        # Filter stages list
        if self.__options.pipeline and self.__options.names and not Lists.match(
                self.__options.names, self.__jobs[job]['stage'],
                ignore_case=self.__options.ignore_case, no_regex=self.__options.no_regex):
            return False

        # Filter manual jobs
        job_manual = (self.__jobs[job]['when'] == 'manual')
        if job_manual and not self.__options.manual and not Lists.match(
                self.__options.names, job, ignore_case=self.__options.ignore_case,
                no_regex=self.__options.no_regex):
            return False

        # Filter disabled jobs
        if self.__jobs[job]['options']['disabled']:
            return False

        # Result
        return True

    # Launch
    def launch(self):

        # Variables
        pipeline_history = PipelineHistory()
        result = None

        # Run selected jobs
        for job in self.__jobs:

            # Filter jobs
            if not self.__filter(job):
                continue

            # Raise initial result
            if result is None:
                result = True

            # Run job
            attempt = 0
            expected = result
            result = Jobs(options=self.__options).run(self.__jobs[job], result,
                                                      pipeline_history)

            # Retry job if allowed
            if expected and not result and self.__jobs[job]['retry'] > 0:
                while not result and attempt < self.__jobs[job]['retry']:
                    attempt += 1
                    result = Jobs(options=self.__options).run(self.__jobs[job], expected,
                                                              pipeline_history)

        # Update pipeline history
        pipeline_history.result = result

        # Non quiet jobs
        if not pipeline_history.jobs_quiet and not self.__options.scripts:

            # Pipeline jobs footer
            if pipeline_history.jobs_count > 1:

                # Output pipeline history
                pipeline_history.print()

            # Footer
            print(' ')
            Platform.flush()

        # Result
        return bool(result)
