#!/usr/bin/env python3

# Standard libraries
from collections import OrderedDict
from itertools import product
from os import environ
from os.path import expandvars
from pathlib import Path
from re import match

# Modules libraries
from dotenv import dotenv_values
from oyaml import safe_load as yaml_safe_load

# Components
from ..containers.images import Images
from ..features.menus import MenusFeature
from ..types.volumes import Volumes

# GitLab class
class GitLab:

    # Constants
    LOCAL_NODE = '.local'

    # Specifications
    JOB_STAGE_DEFAULT = 'test'
    STAGE_POST = '.post'
    STAGE_PRE = '.pre'
    STAGES_DEFAULT = {
        STAGE_PRE: 1,
        'build': 2,
        'test': 3,
        'deploy': 4,
        STAGE_POST: 5,
    }

    # Environment
    ENV_JOB_NAME = 'CI_JOB_NAME'
    ENV_PROJECT_DIR = 'CI_PROJECT_DIR'

    # Members
    __options = None

    # Constructor
    def __init__(self, options):

        # Prepare options
        self.__options = options

    # Merges
    @staticmethod
    def __merges(data, additions):

        # Validate additions
        if not additions or not isinstance(additions, dict):
            return

        # Merge data
        for key in additions:

            # Handle included expanding data
            if key in data and isinstance(additions[key], dict) and key in ['variables']:
                data[key].update(additions[key])

            # Handle included overriding data
            else:
                data[key] = additions[key]

    # Scripts
    @staticmethod
    def __scripts(items):

        # Variables
        scripts = []

        # Parse scripts data
        if isinstance(items, str):
            scripts = [items]
        elif isinstance(items, list):
            scripts = []
            for item in items:
                if isinstance(item, str):
                    scripts += [item]
                elif isinstance(item, list):
                    scripts += item[:]

        # Result
        return scripts

    # Globals, pylint: disable=too-many-branches
    @staticmethod
    def __globals(data, global_values, stages):

        # Parse image node
        if 'image' in data:
            GitLab.__globals_image(data['image'], global_values)

        # Parse before_script node
        if 'before_script' in data:
            global_values['before_script'] = GitLab.__scripts(data['before_script'])

        # Parse after_script node
        if 'after_script' in data:
            global_values['after_script'] = GitLab.__scripts(data['after_script'])

        # Parse services node
        if 'services' in data and isinstance(data['services'], list):
            GitLab.__globals_services(data['services'], global_values)

        # Parse stages node
        if 'stages' in data:
            stages.clear()
            stages[GitLab.STAGE_PRE] = len(stages) + 1
            for _, stage in enumerate(data['stages']):
                if stage is not GitLab.STAGE_PRE and stage is not GitLab.STAGE_POST:
                    stages[stage] = len(stages) + 1
            stages[GitLab.STAGE_POST] = len(stages) + 1

        # Parse variables node
        if 'variables' in data:
            GitLab.__globals_variables(data['variables'], global_values)

        # Parse default node
        if 'default' in data:

            # Parse default image node
            if 'image' in data['default']:
                if 'image' in data:
                    raise SyntaxError(
                        'image is defined in top-level and `default:` entry')
                GitLab.__globals_image(data['default']['image'], global_values)

            # Parse default before_script node
            if 'before_script' in data['default']:
                if 'before_script' in data:
                    raise SyntaxError(
                        'before_script is defined in top-level and `default:` entry')
                global_values['before_script'] = GitLab.__scripts(
                    data['default']['before_script'])

            # Parse default after_script node
            if 'after_script' in data['default']:
                if 'after_script' in data:
                    raise SyntaxError(
                        'after_script is defined in top-level and `default:` entry')
                global_values['after_script'] = GitLab.__scripts(
                    data['default']['after_script'])

            # Parse default services node
            if 'services' in data['default'] and isinstance(data['default']['services'],
                                                            list):
                if 'services' in data:
                    raise SyntaxError(
                        'services is defined in top-level and `default:` entry')
                GitLab.__globals_services(data['default']['services'], global_values)

    # Globals image
    @staticmethod
    def __globals_image(image_data, global_values):

        # Parse image data
        if not global_values['image']:
            if isinstance(image_data, dict):
                global_values['image'] = expandvars(image_data['name'])
                if 'entrypoint' in image_data and len(image_data['entrypoint']) > 0:
                    global_values['entrypoint'] = image_data['entrypoint'][:]
                else:
                    global_values['entrypoint'] = None
            else:
                global_values['image'] = expandvars(image_data)
                global_values['entrypoint'] = None

    # Globals services
    @staticmethod
    def __globals_services(services_data, global_values):

        # Parse services data
        global_values['services'] = []
        for item in services_data:
            if isinstance(item, dict):
                global_values['services'] += [{
                    'image': expandvars(item.get('name', '')),
                    'alias': item.get('alias', ''),
                }]
            elif isinstance(item, str):
                global_values['services'] += [{
                    'image': expandvars(item),
                    'alias': '',
                }]

    # Globals variables
    @staticmethod
    def __globals_variables(variables_data, global_values):

        # Parse variables data
        for variable in variables_data:
            if variable not in global_values['variables']:
                if variables_data[variable] is None:
                    global_values['variables'][variable] = ''
                else:
                    global_values['variables'][variable] = str(variables_data[variable])

    # Include
    def __include(self, data):

        # Parse nested include
        if 'include' in data and data['include']:
            data_new = {}

            # Prepare includes nodes
            data_include_list = []
            if isinstance(data['include'], dict):
                data_include_list = [data['include']]
            elif isinstance(data['include'], list):
                data_include_list = data['include']
            elif isinstance(data['include'], str):
                data_include_list = [{'local': data['include']}]

            # Iterate through includes nodes
            for include_node in data_include_list:

                # Parse local nodes
                if 'local' in include_node:
                    file_path = include_node['local'].lstrip('/')
                    if (Path(self.__options.path) / file_path).is_file():
                        with open(
                                Path(self.__options.path) / file_path, encoding='utf8',
                                mode='r') as include_data:
                            include_additions = yaml_safe_load(include_data)
                            self.__merges(data_new, include_additions)

            # Agregate included data
            self.__merges(data_new, data)
            data = data_new
            data_new = None

        # Result
        return data

    # Local, pylint: disable=too-many-branches,too-many-statements
    def __local(self, data, global_values):

        # Variables
        names_local = False

        # Filter local node, pylint: disable=too-many-nested-blocks
        if GitLab.LOCAL_NODE in data and data[GitLab.LOCAL_NODE]:
            local = data[GitLab.LOCAL_NODE]

            # Parse local after
            if 'after' in local:
                if self.__options.after:
                    self.__options.after = local['after']

            # Parse local all
            if 'all' in local:
                if not self.__options.all:
                    self.__options.all = local['all']

            # Parse local bash
            if 'bash' in local:
                if not self.__options.bash:
                    self.__options.bash = local['bash']

            # Parse local before
            if 'before' in local:
                if self.__options.before:
                    self.__options.before = local['before']

            # Parse local debug
            if 'debug' in local:
                if not self.__options.debug:
                    self.__options.debug = local['debug']

            # Parse local defaults
            if 'defaults' in local:
                if not self.__options.defaults:
                    self.__options.defaults = local['defaults']

            # Parse local engine
            if 'engine' in local:
                if self.__options.engine_default:
                    self.__options.engine = local['engine']
                    self.__options.engine_default = False

            # Parse local env
            if 'env' in local:
                for env in local['env']:
                    env_parsed = env.split('=', 1)

                    # Parse VARIABLE=value
                    if len(env_parsed) == 2:
                        variable = env_parsed[0]
                        value = env_parsed[1]
                        if variable not in global_values['variables']:
                            environ[variable] = value
                            global_values['variables'][variable] = value

                    # Parse ENVIRONMENT_FILE
                    elif (Path(self.__options.path) / env).is_file():
                        environment_file = Path(self.__options.path) / env
                        environment_file_values = dotenv_values(
                            dotenv_path=environment_file)
                        for variable in environment_file_values:

                            # Define default environment variable
                            if variable not in global_values['variables']:
                                global_values['variables'][
                                    variable] = environment_file_values[variable]

                    # Parse VARIABLE
                    else:
                        variable = env
                        if variable not in global_values['variables']:
                            if variable in environ:
                                global_values['variables'][variable] = environ[variable]
                            else:
                                global_values['variables'][variable] = ''

            # Parse local image
            if 'image' in local:
                if not self.__options.image:
                    self.__options.image = local['image']

            # Parse local manual
            if 'manual' in local:
                if not self.__options.manual:
                    self.__options.manual = local['manual']

            # Parse local names
            if 'names' in local:
                if not self.__options.names and not self.__options.pipeline:
                    names_local = True
                    self.__options.names = local['names']

            # Parse local network
            if 'network' in local:
                if not self.__options.network:
                    self.__options.network = local['network']

            # Parse local pipeline
            if 'pipeline' in local:
                if not self.__options.pipeline and (not self.__options.names
                                                    or names_local):
                    self.__options.pipeline = local['pipeline']

            # Parse local quiet
            if 'quiet' in local:
                if not self.__options.quiet:
                    self.__options.quiet = local['quiet']

            # Parse local real_paths
            if 'real_paths' in local:
                if not self.__options.real_paths:
                    self.__options.real_paths = local['real_paths']

            # Parse local sockets
            if 'sockets' in local:
                if not self.__options.sockets:
                    self.__options.sockets = local['sockets']

            # Parse local tags
            if 'tags' in local:
                if self.__options.tags_default:
                    self.__options.tags = local['tags'][:]
                    self.__options.tags_default = False

            # Parse local volumes
            if 'volumes' in local:
                if not self.__options.volume:
                    self.__options.volume = []
                for volume in local['volumes']:
                    self.__options.volume += [Volumes.LOCAL_FLAG + volume]

            # Parse local workdir
            if 'workdir' in local:
                if not self.__options.workdir:
                    self.__options.workdir = Volumes.LOCAL_FLAG + local['workdir']

            # Parse local configurations
            if 'configurations' in local:
                configured_variables = MenusFeature(options=self.__options).configure(
                    local['configurations'])
                global_values['variables'].update(configured_variables)

    # Variants
    @staticmethod
    def __variants(data, node):

        # Variables
        variants = []

        # Handle matrix variants list
        if 'parallel' in data[node] and 'matrix' in data[node]['parallel']:

            # Iterate through matrix items
            for matrix_item in data[node]['parallel']['matrix']:

                # Prepare matrix environments
                matrix_item_environments = []
                matrix_item_environment = {}

                # Iterate through matrix item variables
                for matrix_variable, matrix_values in matrix_item.items():

                    # Already defined environment variable
                    if matrix_variable in environ:
                        matrix_item_environment[matrix_variable] = [
                            environ[matrix_variable]
                        ]

                    # Matrix defined environment variable
                    else:
                        matrix_item_environment[matrix_variable] = []
                        for matrix_value in matrix_values:
                            matrix_item_environment[matrix_variable] += [matrix_value]

                # Register all item combinations
                keys, values = zip(*matrix_item_environment.items())
                matrix_item_environments = [dict(zip(keys, v)) for v in product(*values)]
                for matrix_item_environment in matrix_item_environments:
                    variants += [{
                        'name': f"{node}: [{', '.join(list(matrix_item_environment.values()))}]",
                        'environment': matrix_item_environment
                    }]

        # Prepare default variants list
        else:
            variants = [{'name': node, 'environment': {}}]

        # Result
        return variants

    # Parse, pylint: disable=too-many-branches
    def parse(self, data, environment):

        # Variables
        global_values = dict({
            'after_script': [],
            'before_script': [],
            'image': '',
            'entrypoint': None,
            'services': [],
            'variables': {}
        })
        jobs = {}
        stages = GitLab.STAGES_DEFAULT.copy()

        # Parse nested include
        data = self.__include(data)

        # Prepare parameters variables
        if environment['parameters']:
            global_values['variables'].update(environment['parameters'])

        # Filter local node
        self.__local(data, global_values)

        # Prepare default variables
        if environment['default']:
            for variable in environment['default']:
                if variable not in global_values['variables']:
                    if variable in environ:
                        global_values['variables'][variable] = environ[variable]
                    else:
                        global_values['variables'][variable] = environment['default'][
                            variable]
                if variable not in environ:
                    environ[variable] = global_values['variables'][variable]

        # Prepare global image
        if self.__options.image:
            if isinstance(self.__options.image, dict):
                global_values['image'] = expandvars(self.__options.image['name'])
                if 'entrypoint' in self.__options.image and len(
                        self.__options.image['entrypoint']) > 0:
                    global_values['entrypoint'] = self.__options.image['entrypoint'][:]
                else:
                    global_values['entrypoint'] = None
            else:
                global_values['image'] = expandvars(self.__options.image)
                global_values['entrypoint'] = None

        # Global nodes
        GitLab.__globals(data, global_values, stages)

        # Prepare environment
        _environ = dict(environ)
        environ.update(global_values['variables'])

        # Iterate through nodes
        for node in data:

            # Ignore global nodes
            if node in [
                    'after_script', 'before_script', 'image', 'include', 'services',
                    'stages', 'variables'
            ]:
                continue

            # Validate job node
            if 'script' not in data[node] and 'extends' not in data[node]:
                continue

            # Ignore template stage
            if node[0:1] == '.':
                continue

            # Nodes variants
            variants = GitLab.__variants(data, node)

            # Iterate through node
            for variant in variants:

                # Acquire variant name
                name = variant['name']

                # Prepare variant environment
                if variant['environment']:
                    node_environ = dict(environ)
                    environ.update(variant['environment'])

                # Register job
                jobs[name] = self.job(node, name, data, global_values)

                # Prepare variant variables
                if variant['environment']:
                    jobs[name]['variables'].update(variant['environment'])

                # Validate job script
                if not jobs[name]['options']['disabled'] and not jobs[name]['script']:
                    raise ValueError(
                        f"Missing \"script\" key for \"{jobs[name]['stage']}" \
                            f" / {jobs[name]['name']}\""
                    )

                # Append unknown stage if required
                if jobs[name]['options']['disabled'] \
                        and jobs[name]['stage'] == GitLab.JOB_STAGE_DEFAULT \
                            and GitLab.JOB_STAGE_DEFAULT not in stages:
                    stages[GitLab.JOB_STAGE_DEFAULT] = list(stages.values())[-1] + 1

                # Validate job stage
                if jobs[name]['stage'] not in stages:
                    raise ValueError(
                        f"Unknown stage \"{jobs[name]['stage']}\"" \
                            f" for \"{jobs[name]['name']}\""
                    )

                # Restore variant environment
                if variant['environment']:
                    environ.clear()
                    environ.update(node_environ)

        # Sort jobs based on stages
        jobs = OrderedDict(sorted(jobs.items(), key=lambda x: stages[x[1]['stage']]))

        # Restore environment
        environ.clear()
        environ.update(_environ)

        # Result
        return jobs

    # Job, pylint: disable=too-many-branches,too-many-statements
    def job(self, job_node, job_name, data, global_values):

        # Variables
        job = {}
        job_data = data[job_node]

        # Prepare stage
        job['name'] = job_name
        job['stage'] = None
        job['image'] = None
        job['entrypoint'] = None
        job['variables'] = None
        job['before_script'] = None
        job['script'] = None
        job['after_script'] = None
        job['retry'] = None
        job['when'] = None
        job['allow_failure'] = None
        job['services'] = None
        job['tags'] = None
        job['trigger'] = None
        job['options'] = {}
        job['options']['disabled'] = None
        job['options']['host'] = False
        job['options']['extends'] = {}
        job['options']['extends']['available'] = []
        job['options']['extends']['unknown'] = []
        job['options']['quiet'] = False
        job['options']['silent'] = False
        job['options']['sockets'] = False
        job['options']['env_job_name'] = self.ENV_JOB_NAME
        job['options']['env_job_path'] = self.ENV_PROJECT_DIR

        # Extract job extends
        if 'extends' in job_data and job_data['extends']:
            if isinstance(job_data['extends'], list):
                job_extends = job_data['extends']
            else:
                job_extends = [job_data['extends']]

            # Iterate through extended jobs
            for job_extend in reversed(job_extends):

                # Validate extended job
                if job_extend not in data:
                    job['options']['extends']['unknown'] += [f'{job_extend} unknown']
                    if job['stage'] is None:
                        job['stage'] = GitLab.JOB_STAGE_DEFAULT
                    continue

                # Parse extended job
                job_extended = self.job(job_extend, job_extend, data, None)

                # List available extended job
                job['options']['extends']['available'] += [job_extend]

                # Extract extended job
                if job['stage'] is None:
                    job['stage'] = job_extended['stage']
                if job['image'] is None:
                    job['image'] = job_extended['image']
                if job['entrypoint'] is None:
                    job['entrypoint'] = job_extended['entrypoint']
                if job['variables'] is None:
                    job['variables'] = job_extended['variables']
                elif job_extended['variables']:
                    for variable in job_extended['variables']:
                        job['variables'][variable] = job_extended['variables'][variable]
                if job['before_script'] is None:
                    job['before_script'] = job_extended['before_script']
                if job['script'] is None:
                    job['script'] = job_extended['script']
                if job['after_script'] is None:
                    job['after_script'] = job_extended['after_script']
                if job['retry'] is None:
                    job['retry'] = job_extended['retry']
                if job['when'] is None:
                    job['when'] = job_extended['when']
                if job['allow_failure'] is None:
                    job['allow_failure'] = job_extended['allow_failure']
                if job['services'] is None:
                    job['services'] = job_extended['services']
                if job['tags'] is None:
                    job['tags'] = job_extended['tags']
                if job['trigger'] is None:
                    job['trigger'] = job_extended['trigger']

            # Detect incomplete extended job
            if job['options']['extends']['unknown'] and \
                    (len(job_extends) == 1 or len(job['options']['extends']['available']) == 0):
                job['options']['disabled'] = ', '.join(
                    job['options']['extends']['unknown'])

        # Apply global values
        if global_values:
            if job['image'] is None:
                job['image'] = global_values['image']
            if job['entrypoint'] is None:
                job['entrypoint'] = global_values['entrypoint'][:] if global_values[
                    'entrypoint'] else None
            if job['variables'] is None:
                job['variables'] = dict(global_values['variables'])
            else:
                for variable in global_values['variables']:
                    if variable not in job['variables']:
                        job['variables'][variable] = global_values['variables'][variable]
            if job['before_script'] is None:
                job['before_script'] = global_values['before_script'][:]
            if job['script'] is None:
                job['script'] = []
            if job['after_script'] is None:
                job['after_script'] = global_values['after_script'][:]
            if job['retry'] is None:
                job['retry'] = 0
            if job['services'] is None:
                job['services'] = global_values['services'][:]
            if job['when'] is None:
                job['when'] = 'on_success'
            if job['allow_failure'] is None:
                job['allow_failure'] = False

        # Apply template values
        else:
            if job['variables'] is None:
                job['variables'] = {}

        # Extract job stage
        if 'stage' in job_data and job_data['stage']:
            job['stage'] = job_data['stage']
        elif job['stage'] is None:
            job['stage'] = GitLab.JOB_STAGE_DEFAULT

        # Extract job image
        if 'image' in job_data and job_data['image']:
            image_data = job_data['image']
            if isinstance(image_data, dict):
                job['image'] = expandvars(image_data['name'])
                if 'entrypoint' in image_data and len(image_data['entrypoint']) > 0:
                    job['entrypoint'] = image_data['entrypoint'][:]
                else:
                    job['entrypoint'] = None
            else:
                job['image'] = expandvars(image_data)
                job['entrypoint'] = None

        # Extract job variables
        if 'variables' in job_data and job_data['variables']:
            for variable in job_data['variables']:
                if job_data['variables'][variable] is None:
                    job['variables'][variable] = ''
                else:
                    job['variables'][variable] = str(job_data['variables'][variable])

        # Extract job before_script
        if 'before_script' in job_data:
            job['before_script'] = self.__scripts(job_data['before_script'])

        # Extract job script
        if 'script' in job_data:
            job['script'] = self.__scripts(job_data['script'])

        # Extract job after_script
        if 'after_script' in job_data:
            job['after_script'] = self.__scripts(job_data['after_script'])

        # Extract job retry
        if 'retry' in job_data:
            retry_data = job_data['retry']
            if isinstance(retry_data, dict):
                job['retry'] = int(retry_data['max'])
            else:
                job['retry'] = int(retry_data)

        # Extract job when
        if 'when' in job_data and job_data['when'] in [
                'on_success', 'on_failure', 'always', 'manual'
        ]:
            job['when'] = job_data['when']

        # Extract job allow_failure
        if 'allow_failure' in job_data and job_data['allow_failure'] in [True, False]:
            job['allow_failure'] = job_data['allow_failure']

        # Extract job services
        if 'services' in job_data and isinstance(job_data['services'], list):
            job['services'] = []
            for item in job_data['services']:
                if isinstance(item, dict):
                    job['services'] += [{
                        'image': expandvars(item.get('name', '')),
                        'alias': item.get('alias', ''),
                    }]
                elif isinstance(item, str):
                    job['services'] += [{
                        'image': expandvars(item),
                        'alias': '',
                    }]

        # Extract job tags
        if 'tags' in job_data and job_data['tags']:
            job['tags'] = job_data['tags'][:]

        # Extract job trigger
        if 'trigger' in job_data and job_data['trigger']:
            job['options']['disabled'] = 'trigger only'
            if isinstance(job_data['trigger'], (dict, str)):
                job['trigger'] = job_data['trigger']

        # Finalize global values
        if global_values:

            # Configure job tags
            if job['tags'] and (set(job['tags']) & set(self.__options.tags)):
                job['when'] = 'manual'

        # Detect host jobs
        if job['image']:
            job['options']['host'] = Images.host(job['image'])
            job['options']['quiet'] = Images.quiet(job['image'])
            job['options']['silent'] = Images.silent(job['image'])

        # Detect sockets services
        if job['services']:
            for service in job['services']:
                if match(Images.DOCKER_DIND_REGEX, service['image']):
                    job['options']['sockets'] = True

        # Apply sockets option
        if not job['options']['sockets']:
            job['options']['sockets'] = self.__options.sockets

        # Result
        return job
