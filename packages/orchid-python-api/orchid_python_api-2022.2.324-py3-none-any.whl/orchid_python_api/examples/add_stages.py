#  Copyright 2017-2022 Reveal Energy Services, Inc 
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

"""
Tutorial demonstrating how to add stages to a well using the high-level (Pythonic) API.
"""

import argparse
import logging
import pathlib


import pendulum


import orchid
from orchid import (
    native_stage_adapter as nsa,
)


def add_stages(project, verbosity):
    """
    Add stages to `project`.

    Args:
        project: The `Project` instance to which I add the stages.
        verbosity: The verbosity of the output.
    """
    # Find well to which to add stages
    candidate_well_name = 'Demo_4H'
    candidate_wells = list(project.wells().find_by_display_name(candidate_well_name))
    assert len(candidate_wells) == 1, (f'Expected single well named "{candidate_well_name}".'
                                       f' Found {len(candidate_wells)}.')
    target_well = candidate_wells[0]

    # Create an iterable of stage DTOs (data transfer objects) to append
    # WARNING: The details of these created stages are reasonable but not necessarily consistent with other stage
    # data in the Bakken project.
    # noinspection PyTypeChecker
    stages_to_append = [
        nsa.CreateStageDto(
            36,  # hard-coded to be one greater than largest `order_of_completion_on_well`
            nsa.ConnectionType.PLUG_AND_PERF,
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 10966.0),
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 11211.0),
            # `pendulum` uses UTC by default for timezone (and UTC required)
            maybe_time_range=pendulum.parse('2018-06-28T22:24:57/2018-06-29T00:10:24'),
            maybe_isip=3420.32 * orchid.unit_registry.psi,
        ),
        nsa.CreateStageDto(
            37,
            nsa.ConnectionType.PLUG_AND_PERF,
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 10672.0),
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 10917.0),
            maybe_shmin=orchid.make_measurement(orchid.unit_system.UsOilfield.PRESSURE, 2.322),
            # `pendulum` uses UTC by default for timezone (and UTC required)
            maybe_time_range=pendulum.parse('2018-06-29T02:27:56/2018-06-29T04:50:17'),
            maybe_isip=2712.70 * orchid.unit_registry.psi,
        ),
        nsa.CreateStageDto(
            38,
            nsa.ConnectionType.PLUG_AND_PERF,
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 10378.0),
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 10623.0),
            cluster_count=7,
            # `pendulum` uses UTC by default for timezone (and UTC required)
            maybe_time_range=pendulum.parse('2018-05-29T06:47:15/2018-06-29T08:44:54'),
            maybe_isip=3192.69 * orchid.unit_registry.psi
        ),
    ]

    # Optionally log details of stages to create
    if verbosity >= 1:
        for stage_dto in stages_to_append:
            logging.info('Adding stage')
            logging.info(stage_dto)

    target_well.add_stages(stages_to_append)


def main(cli_args):
    """
    Add stages to an existing project and save changes back to disk.

    Args:
        cli_args: The command line arguments from `argparse.ArgumentParser`.
    """
    logging.basicConfig(level=logging.INFO)

    # Read Orchid project
    project = orchid.load_project(cli_args.input_project)

    add_stages(project, cli_args.verbosity)

    # Save project changes to specified .ifrac file
    orchid.optimized_but_possibly_unsafe_save(project, cli_args.input_project, cli_args.output_project)
    if cli_args.verbosity >= 1:
        logging.info(f'Wrote changes to "{cli_args.output_project}"')


def make_project_path_name(project_dir_name, project_file_name):
    """
    Make a path name to a project.

    Args:
        project_dir_name: The directory name of the project.
        project_file_name: The file name of the project.

    Returns:
        The path name to the .ifrac file for this project.
    """
    return str(project_dir_name.joinpath(project_file_name))


def make_target_file_name_from_source(source_file_name):
    """
    Make a file name for the changed project file name from the original project file name.

    Args:
        source_file_name: The file name of the project originally read.

    Returns:
        The project file name with a `.993` suffix inserted before the `.ifrac` suffix.
    """
    return ''.join([source_file_name.stem, '.993', source_file_name.suffix])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Adds newly created stages to a well in a project")
    parser.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2], default=0,
                        help='Increase output verbosity. (Default: 0; that is, least output.)')

    parser.add_argument('input_project', help=f'Path name of project to read.')

    # Although input file must be 'frankNstein_Bakken_UTM13_FEET.v11.ifrac', I use the original version as the
    # default for the correct output file name.
    default_file_name_to_read = pathlib.Path('frankNstein_Bakken_UTM13_FEET.ifrac')
    default_project_path_name_to_read = make_project_path_name(orchid.training_data_path(),
                                                               default_file_name_to_read)
    default_file_name_to_write = make_target_file_name_from_source(default_file_name_to_read)
    default_project_path_name_to_write = make_project_path_name(orchid.training_data_path(),
                                                                default_file_name_to_write)
    parser.add_argument('-o', '--output_project', default=default_project_path_name_to_write,
                        help=f'Filename of project to write. (Default: {default_project_path_name_to_write}')

    args = parser.parse_args()
    main(args)
