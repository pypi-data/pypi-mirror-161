#
# This file is part of Orchid and related technologies.
#
# Copyright (c) 2017-2022 Reveal Energy Services.  All Rights Reserved.
#
# LEGAL NOTICE:
# Orchid contains trade secrets and otherwise confidential information
# owned by Reveal Energy Services. Access to and use of this information is 
# strictly limited and controlled by the Company. This file may not be copied,
# distributed, or otherwise disclosed outside of the Company's facilities 
# except under appropriate precautions to maintain the confidentiality hereof, 
# and may not be used in any way not expressly authorized by the Company.
#

"""
Changes the start and stop times (time range) of a stage using the high-level Python API.
"""

import argparse
import logging
import pathlib

import pendulum  # Used for creating time-zone aware date times (UTC by default)

import orchid
from orchid import (
    net_fracture_diagnostics_factory as net_factory,
)


object_factory = net_factory.create()


def change_stage_time_range(project):
    # Get stage
    candidate_wells = list(project.wells().find_by_name('Demo_1H'))
    well_of_interest = candidate_wells[0]

    stage = well_of_interest.stages().find_by_display_stage_number(1)

    # Start time before change
    ante_start_time = stage.start_time
    ante_stop_time = stage.stop_time
    logging.info(f'Stage time_range before {pendulum.Period(ante_start_time, ante_stop_time)}')

    post_start_time = ante_start_time.subtract(minutes=10)
    post_stop_time = ante_stop_time.add(minutes=10)
    stage.time_range = pendulum.Period(post_start_time, post_stop_time)
    logging.info(f'Stage time_range after {stage.time_range}')


def main(cli_args):
    """
    Change stage start/stop times of stage 1 of well, `Demo_1H`.

    Args:
        cli_args: The command line arguments from `argparse.ArgumentParser`.
    """
    logging.basicConfig(level=logging.INFO)

    # Read Orchid project
    project = orchid.load_project(cli_args.input_project)

    change_stage_time_range(project)

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
        The project file name with a `.995` suffix inserted before the `.ifrac` suffix.
    """
    return ''.join([source_file_name.stem, '.995', source_file_name.suffix])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Change stage start and stop times using the high-level API.")
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

