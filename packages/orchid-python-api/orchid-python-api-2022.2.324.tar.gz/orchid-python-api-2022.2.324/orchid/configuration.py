#  Copyright (c) 2017-2022 Reveal Energy Services, Inc 
#
#  Licensed under the Apache License, Version 2.0 (the "License"); 
#  you may not use this file except in compliance with the License. 
#  You may obtain a copy of the License at 
#
#      http://www.apache.org/licenses/LICENSE-2.0 
#
#  Unless required by applicable law or agreed to in writing, software 
#  distributed under the License is distributed on an "AS IS" BASIS, 
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
#  See the License for the specific language governing permissions and 
#  limitations under the License. 
#
# This file is part of Orchid and related technologies.
#

import glob
import logging
import os
import pathlib
from typing import Dict
import warnings

import toolz.curried as toolz
import yaml

import orchid.version


_logger = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


# Constants for environment variable names
ORCHID_ROOT_ENV_VAR = 'ORCHID_ROOT'
ORCHID_TRAINING_DATA_ENV_VAR = 'ORCHID_TRAINING_DATA'


def get_environment_configuration() -> Dict:
    """
    Gets the API configuration from the system environment.

    Returns:
        The configuration, if any, calculated from the system environment.
    """
    environment_configuration = {}
    if ORCHID_ROOT_ENV_VAR in os.environ and ORCHID_TRAINING_DATA_ENV_VAR in os.environ:
        environment_configuration = {'orchid': {'root': os.environ[ORCHID_ROOT_ENV_VAR],
                                                'training_data': os.environ[ORCHID_TRAINING_DATA_ENV_VAR]}}
    elif ORCHID_ROOT_ENV_VAR in os.environ:
        environment_configuration = {'orchid': {'root': os.environ[ORCHID_ROOT_ENV_VAR]}}
    elif ORCHID_TRAINING_DATA_ENV_VAR in os.environ:
        environment_configuration = {'orchid': {'training_data': os.environ[ORCHID_TRAINING_DATA_ENV_VAR]}}

    _logger.debug(f'environment configuration = {environment_configuration}')

    return environment_configuration


def get_fallback_configuration() -> Dict:
    """
    Returns final fallback API configuration.

    Returns:
        A Python dictionary with the default (always available configuration).

    Warning:
        Although we have striven to make the default configuration a working configuration, we can only ensure
        that the default configuration meets the minimal "syntax" required by the Python API. For example, if
        Orchid is **not** installed in the default location, and the `directory` key is not overridden by a
        higher priority configuration, the Python API will **fail** to load the Orchid assemblies and throw
        an exception at runtime.
    """

    # Symbolically, the standard location for the installed Orchid binaries is
    # `$ProgramFiles/Reveal Energy Services, Inc/Orchid/<version-specific-directory>`. The following code
    # calculates an actual location by substituting the current version number for the symbol,
    # `<version-specific-directory>`.
    standard_orchid_dir = pathlib.Path(os.environ['ProgramFiles']).joinpath('Reveal Energy Services',
                                                                            'Orchid')
    version_id = orchid.version.api_version()
    version_dirname = f'Orchid-{version_id.major}.{version_id.minor}.{version_id.micro}'
    glob_path = standard_orchid_dir.joinpath(f'{version_dirname}*', 'PythonApiLibs')
    candidate_directories = glob.glob(str(glob_path))
    if len(candidate_directories) == 1:
        fallback = {'orchid': {'root': str(candidate_directories[0])}}
    elif len(candidate_directories) == 0:
        fallback = {}
    else:
        fallback = {}
        warnings.warn(f'Fallback configuration found multiple matches for {str(glob_path)}')
    _logger.debug(f'fallback configuration={fallback}')
    return fallback


def get_file_configuration() -> Dict:
    """
    Returns the API configuration read from the file system.

    Returns:
        A python dictionary with the default (always available configuration).
    """

    # This code looks for the configuration file, `python_api.yaml`, in the `.orchid` sub-directory of the
    # user-specific (and system-specific) home directory. See the Python documentation of `home()` for
    # details.
    file = {}
    file_config_path = pathlib.Path.home().joinpath('.orchid', 'python_api.yaml')
    if file_config_path.exists():
        with file_config_path.open('r') as in_stream:
            file = yaml.full_load(in_stream)
    _logger.debug(f'file configuration={file}')
    return file


def python_api() -> Dict[str, str]:
    """
    Calculate the configuration for the Python API.

        Returns: The Python API configuration.
    """

    fallback_configuration = get_fallback_configuration()
    file_configuration = get_file_configuration()
    env_configuration = get_environment_configuration()

    result = merge_configurations(fallback_configuration, file_configuration, env_configuration)
    _logger.debug(f'result configuration={result}')
    return result


def merge_configurations(fallback_configuration, file_configuration, env_configuration):
    # The rules for merging these configurations is not the same as a simple dictionary. The rules are:
    # - If two different configurations share a top-level key, merge the second level dictionaries.
    # - Then merge the distinct top-level keys.
    distinct_top_level_keys = set(toolz.concat([fallback_configuration.keys(),
                                                file_configuration.keys(),
                                                env_configuration.keys()]))
    result = {}
    for top_level_key in distinct_top_level_keys:
        fallback_child_configuration = fallback_configuration.get(top_level_key, {})
        file_child_configuration = file_configuration.get(top_level_key, {})
        env_child_configuration = env_configuration.get(top_level_key, {})
        child_configuration = toolz.merge(fallback_child_configuration,
                                          file_child_configuration,
                                          env_child_configuration)
        result[top_level_key] = child_configuration
    return result


def training_data_path() -> pathlib.Path:
    """
    Returns the path of the directory containing the Orchid training data.

    Returns:
        The Orchid training data path.

    Raises:
        This function raises KeyError if the training directory path is not available from the package
        configuration.
    """
    result = pathlib.Path(toolz.get_in(['orchid', 'training_data'], python_api()))
    return result
