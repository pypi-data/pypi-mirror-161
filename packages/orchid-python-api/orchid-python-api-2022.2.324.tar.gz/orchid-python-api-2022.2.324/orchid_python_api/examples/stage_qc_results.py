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

"""Demonstrates using the high-level Orchid Python API to query and change the stage QC status."""

import argparse
import dataclasses as dc
import logging
import pathlib
from typing import Iterable

import orchid
from orchid import (
    project as op,
    net_stage_qc as nqc,
)


@dc.dataclass
class WellStagePair:
    well_name: str
    stage_no: int


@dc.dataclass
class StageQCInfo:
    start_stop_confirmation: nqc.CorrectionStatus
    stage_qc_notes: str


@dc.dataclass
class StageQCResult:
    well_stage_pair: WellStagePair
    stage_qc_info: StageQCInfo


def read_stage_qc(project: op.Project, sample_stages: Iterable[WellStagePair]) -> Iterable[StageQCResult]:
    """
    Read the stage QC result for each item of `sample_stages` of `project`.

    Args:
        project: The project of interest
        sample_stages: The iterable returning each `WellStagePair` whose stage QC results are sought.

    Returns:
        An iterable containing the `StageQCResult` for each `WellStagePair`
    """
    def read_stage_cq_result(project: op.Project, well_name_stage_pair: WellStagePair) -> StageQCResult:
        candidate_wells = list(project.wells().find_by_name(well_name_stage_pair.well_name))
        assert len(candidate_wells) == 1, (f'Expected 1 well with name, {well_name_stage_pair.well_name}.'
                                           f' Found {len(candidate_wells)}.')
        well = candidate_wells[0]
        stage = well.stages().find_by_display_stage_number(well_name_stage_pair.stage_no)

        project_user_data = project.user_data
        qc_notes = project_user_data.stage_qc_notes(stage.object_id)
        start_stop_confirmation = project_user_data.stage_start_stop_confirmation(stage.object_id)

        return StageQCResult(well_name_stage_pair, StageQCInfo(start_stop_confirmation=start_stop_confirmation,
                                                               stage_qc_notes=qc_notes))

    result = [read_stage_cq_result(project, wsp) for wsp in sample_stages]
    return result


def log_stage_qc_results(stage_qc_results: Iterable[StageQCResult], prefix: str) -> None:
    """
    Logs each item in `stage_qc_results`.

    Args:
        stage_qc_results: An iterable of `StageQCResult` instances.
        prefix: Text to write before writing the results.
    """
    logging.info(prefix)
    for stage_qc_result in stage_qc_results:
        logging.info(stage_qc_result)


def change_stage_qc(project: op.Project, to_stage_qc_results: Iterable[StageQCResult]) -> None:
    """
    Changes the stage QC results of `project` to `to_stage_qc_results`.

    Args:
        project: The project whose stage QC results are to be changed.
        to_stage_qc_results: The revised stage QC results.
    """
    for to_stage_qc_result in to_stage_qc_results:
        candidate_wells = list(project.wells().find_by_name(to_stage_qc_result.well_stage_pair.well_name))
        assert len(candidate_wells) == 1, (f'Expected 1 well with name,'
                                           f' {to_stage_qc_result.well_stage_pair.well_name}.'
                                           f' Found {len(candidate_wells)}.')
        well = candidate_wells[0]
        stage = well.stages().find_by_display_stage_number(to_stage_qc_result.well_stage_pair.stage_no)

        project_user_data = project.user_data
        project_user_data.set_stage_qc_notes(stage.object_id, to_stage_qc_result.stage_qc_info.stage_qc_notes)
        project_user_data.set_stage_start_stop_confirmation(stage.object_id,
                                                            to_stage_qc_result.stage_qc_info.start_stop_confirmation)


def main(cli_args):
    """
    Change stage start/stop times of stage 1 of well, `Demo_1H`.

    Args:
        cli_args: The command line arguments from `argparse.ArgumentParser`.
    """
    logging.basicConfig(level=logging.INFO)

    # Read Orchid project
    project = orchid.load_project(cli_args.input_project)

    # If no stages have undergone the stage QC process (like this project), reading the stage QC information produces
    # "uninteresting" results.
    sample_stages = [WellStagePair('Demo_1H', 9),
                     WellStagePair('Demo_2H', 7),
                     WellStagePair('Demo_4H', 23)]
    uninteresting_stage_qc_results = read_stage_qc(project, sample_stages)
    if cli_args.verbosity >= 1:
        log_stage_qc_results(uninteresting_stage_qc_results,
                             f'Reading results from input file: {cli_args.input_project}')

    if not cli_args.read_only:
        # Change the stage QC information of these same stages to be "interesting"
        to_stage_qc_info = [StageQCInfo(nqc.CorrectionStatus.UNCONFIRMED, stage_qc_notes='Strange'),
                            StageQCInfo(nqc.CorrectionStatus.CONFIRMED, stage_qc_notes='Good stage'),
                            StageQCInfo(nqc.CorrectionStatus.NEW, stage_qc_notes='')]
        to_stage_qc_results = [StageQCResult(wsp, info) for wsp, info in zip(sample_stages, to_stage_qc_info)]
        change_stage_qc(project, to_stage_qc_results)

        # Reading these same stages now produces "interesting" results
        interesting_stage_qc_results = read_stage_qc(project, sample_stages)
        if cli_args.verbosity >= 1:
            log_stage_qc_results(interesting_stage_qc_results, f'Reading results after change:')

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
        The project file name with a `.994` suffix inserted before the `.ifrac` suffix.
    """
    return ''.join([source_file_name.stem, '.994', source_file_name.suffix])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Demonstrate reading and updating stage QC information.")
    parser.add_argument('-r', '--read-only', action='store_true', default=False,
                        help='Only read the stage QC results.')
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

