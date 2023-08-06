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
Example of adding stages to a project using the low-level (Python.NET) API.
"""


import argparse
from collections import namedtuple
import dataclasses as dc
import logging
import pathlib
from typing import Optional

import pendulum  # Used for creating time-zone aware date times (UTC by default)

import orchid
from orchid import (
    dot_net_disposable as dnd,
    native_stage_adapter as nsa,
    native_well_adapter as nwa,
    net_fracture_diagnostics_factory as net_factory,
    net_quantity as onq,
    net_date_time as ndt,
    measurement as om,
    unit_system as units,
)

import clr
clr.AddReference('System.Collections')

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import (IStage, IStagePart)
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.SDKFacade import ScriptAdapter
# noinspection PyUnresolvedReferences
from System import (Array, UInt32, Nullable,)
# noinspection PyUnresolvedReferences
from System.Collections.Generic import List
# noinspection PyUnresolvedReferences
from UnitsNet import Pressure


object_factory = net_factory.create()


@dc.dataclass
class CreateStageDto:
    order_of_completion_on_well: int  # Must be non-negative
    connection_type: nsa.ConnectionType
    md_top: om.Quantity  # Must be length
    md_bottom: om.Quantity  # Must be length
    maybe_shmin: Optional[om.Quantity] = None  # If not None, must be pressure
    cluster_count: int = 0  # Must be non-negative
    # WARNING: one need supply neither a start time nor a stop time; however, not supplying this data can
    # produce unexpected behavior for the `global_stage_sequence_number` property. For example, one can
    # generate duplicate values for the `global_stage_sequence_number`. This unexpected behavior is a known
    # issue with Orchid.
    #
    # Note supplying no value (an implicit `None`) results in the largest possible .NET time range.
    maybe_time_range: Optional[pendulum.Period] = None

    # WARNING: one must currently supply an ISIP for each stage; otherwise, Orchid fails to correctly load
    # the project saved with the added stages.
    maybe_isip: Optional[om.Quantity] = None  # The actual value must be a pressure

    def create_stage(self, well: nwa.NativeWellAdapter):
        # Must supply the unit system for conversions
        native_md_top = onq.as_net_quantity(units.UsOilfield.LENGTH, self.md_top)
        native_md_bottom = onq.as_net_quantity(units.UsOilfield.LENGTH, self.md_bottom)
        native_shmin = (ScriptAdapter.MakeOptionSome(onq.as_net_quantity(units.UsOilfield.PRESSURE,
                                                                         self.maybe_shmin))
                        if self.maybe_shmin is not None
                        else ScriptAdapter.MakeOptionNone[Pressure]())
        no_time_range_native_stage = object_factory.CreateStage(
            UInt32(self.order_of_completion_on_well),
            well.dom_object,
            self.connection_type.value,
            native_md_top,
            native_md_bottom,
            native_shmin,
            UInt32(self.cluster_count)
        )
        with dnd.disposable(no_time_range_native_stage.ToMutable()) as mutable_stage:
            if self.maybe_time_range is not None:
                stage_part = object_factory.CreateStagePart(no_time_range_native_stage,
                                                            ndt.as_net_date_time(self.maybe_time_range.start),
                                                            ndt.as_net_date_time(self.maybe_time_range.end),
                                                            onq.as_net_quantity_in_specified_unit(
                                                                units.UsOilfield.PRESSURE, self.maybe_isip))
                stage_parts = List[IStagePart]()
                stage_parts.Add(stage_part)
                mutable_stage.Parts = stage_parts
        native_stage = no_time_range_native_stage

        return nsa.NativeStageAdapter(native_stage)

    def __post_init__(self):
        # See the
        # [StackOverflow post](https://stackoverflow.com/questions/54488765/validating-input-when-mutating-a-dataclass)
        assert self.order_of_completion_on_well >= 0, f'order_of_completion_on_well must be non-zero'
        assert self.md_top.check('[length]'), f'md_top must be a length'
        assert self.md_bottom.check('[length]'), f'md_bottom must be a length'
        if self.maybe_shmin is not None:
            assert self.maybe_shmin.check('[pressure]'), f'maybe_shmin must be a pressure if not `None`'
        assert self.cluster_count >= 0, f'cluster_count must be non-zero'
        if self.maybe_isip is not None:
            assert self.maybe_isip.check('[pressure]'), f'maybe_isip must be a pressure if not `None`'


CreatedStageDetails = namedtuple('CreatedStageDetails', ['name', 'shmin', 'cluster_count',
                                                         'global_stage_sequence_no', 'start_time', 'stop_time'])


def add_stages(project):
    # Find well to which to add stages
    candidate_well_name = 'Demo_4H'
    candidate_wells = list(project.wells().find_by_display_name(candidate_well_name))
    assert len(candidate_wells) == 1, (f'Expected single well named "{candidate_well_name}".'
                                       f' Found {len(candidate_wells)}.')
    target_well = candidate_wells[0]

    # Create an iterable of stages to append
    stages_to_append = [
        CreateStageDto(
            35,  # hard-coded to be one greater than largest `order_of_completion_on_well`
            nsa.ConnectionType.PLUG_AND_PERF,
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 20898.2),
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 20985.8),
            # `pendulum` uses UTC by default for timezone (and UTC required)
            maybe_time_range=pendulum.parse('2018-06-06T05:34:03.6839387/2018-06-06T07:19:35.5601864'),
            maybe_isip=3420.32 * orchid.unit_registry.psi,
        ),
        CreateStageDto(
            36,
            nsa.ConnectionType.PLUG_AND_PERF,
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 17362.2),
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 17372.3),
            maybe_shmin=orchid.make_measurement(orchid.unit_system.UsOilfield.PRESSURE, 2.322),
            # `pendulum` uses UTC by default for timezone (and UTC required)
            maybe_time_range=pendulum.parse('2018-06-15T14:11:40.450044/2018-06-15T15:10:11.200044'),
            maybe_isip=2712.70 * orchid.unit_registry.psi,
        ),
        CreateStageDto(
            37,
            nsa.ConnectionType.PLUG_AND_PERF,
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 10627.2),
            orchid.make_measurement(orchid.unit_system.UsOilfield.LENGTH, 10759.7),
            cluster_count=7,
            # `pendulum` uses UTC by default for timezone (and UTC required)
            maybe_time_range=pendulum.parse('2018-06-28T23:35:54.3790545/2018-06-29T01:18:05.8397489'),
            maybe_isip=3192.69 * orchid.unit_registry.psi
        ),
    ]
    created_stages = [stage_dto.create_stage(target_well) for stage_dto in stages_to_append]

    for created_stage in created_stages:
        logging.info(CreatedStageDetails(created_stage.name,
                                         f'{created_stage.shmin:.3f~P}' if created_stage.shmin else 'None',
                                         created_stage.cluster_count,
                                         created_stage.global_stage_sequence_number,
                                         str(created_stage.start_time),
                                         str(created_stage.stop_time)))

    # Add stages to target_well
    with dnd.disposable(target_well.dom_object.ToMutable()) as mutable_well:
        native_created_stages = Array[IStage]([created_stage.dom_object for created_stage in created_stages])
        mutable_well.AddStages(native_created_stages)


def main(cli_args):
    """
    Add stages to an existing project and save changes back to disk.

    Args:
        cli_args: The command line arguments from `argparse.ArgumentParser`.
    """
    logging.basicConfig(level=logging.INFO)

    # Read Orchid project
    project = orchid.load_project(cli_args.input_project)

    add_stages(project)

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
        The project file name with a `.996` suffix inserted before the `.ifrac` suffix.
    """
    return ''.join([source_file_name.stem, '.996', source_file_name.suffix])


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

