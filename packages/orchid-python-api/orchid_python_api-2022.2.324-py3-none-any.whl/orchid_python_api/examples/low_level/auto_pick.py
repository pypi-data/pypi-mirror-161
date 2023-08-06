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

import argparse
import functools
import logging
import pathlib

import clr
import orchid
from orchid import (
    dot_net_disposable as dnd,
    net_fracture_diagnostics_factory as net_factory,
)

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import (MonitorExtensions, Leakoff, Observation)
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.Factories.Implementations import LeakoffCurves
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.SDKFacade import (
    ScriptAdapter,
)
# noinspection PyUnresolvedReferences
from System import (Array, Double, DateTime, String)
# noinspection PyUnresolvedReferences
from System.IO import (FileStream, FileMode, FileAccess, FileShare)
# noinspection PyUnresolvedReferences
import UnitsNet

clr.AddReference('Orchid.Math')
clr.AddReference('System.Collections')
# noinspection PyUnresolvedReferences
from Orchid.Math import Interpolation
# noinspection PyUnresolvedReferences
from System.Collections.Generic import List


object_factory = net_factory.create()


def calculate_delta_pressure(leak_off_pressure, maximum_pressure_sample):
    """
    Calculate the delta pressure value.

    Args:
        leak_off_pressure: Pressure from the treatment leak off curve.
        maximum_pressure_sample: The maximum treatment pressure.

    Returns:
        The pressure difference.

    """
    return UnitsNet.Pressure.op_Subtraction(
        UnitsNet.Pressure(maximum_pressure_sample.Value, UnitsNet.Units.PressureUnit.PoundForcePerSquareInch),
        leak_off_pressure)


def calculate_leak_off_control_point_times(interpolation_point_1, interpolation_point_2, ticks):
    """
    Return the calculated control points for a leak off curve.

    Args:
        interpolation_point_1: The first point at which to interpolate pressure values.
        interpolation_point_2: The second point at which to interpolate pressure values.
        ticks: A sequence of .NET `Tick` values.

    Returns:
        The times at which to set the control points for a leak off curve.
    """
    time_series_interpolation_points = Array.CreateInstance(Double, 2)
    time_series_interpolation_points[0] = interpolation_point_1.Ticks
    time_series_interpolation_points[1] = interpolation_point_2.Ticks
    time_stamp_ticks = Array.CreateInstance(Double, ticks.Length)
    magnitudes = Array.CreateInstance(Double, ticks.Length)
    for i in range(0, ticks.Length):
        tick = ticks[i]
        time_stamp_ticks[i] = tick.Timestamp.Ticks
        magnitudes[i] = tick.Value
    time_series_interpolant = Interpolation.Interpolant1DFactory.CreatePchipInterpolant(time_stamp_ticks,
                                                                                        magnitudes)
    pressure_values = time_series_interpolant.Interpolate(time_series_interpolation_points, 0)
    control_point_times = List[Leakoff.ControlPoint]()
    control_point_times.Add(Leakoff.ControlPoint(
        DateTime=interpolation_point_1,
        Pressure=UnitsNet.Pressure(pressure_values[0], UnitsNet.Units.PressureUnit.PoundForcePerSquareInch)))
    control_point_times.Add(Leakoff.ControlPoint(
        DateTime=interpolation_point_2,
        Pressure=UnitsNet.Pressure(pressure_values[1], UnitsNet.Units.PressureUnit.PoundForcePerSquareInch)))
    return control_point_times


def calculate_leak_off_pressure(leak_off_curve, maximum_pressure_sample):
    """
    Calculate the leak off pressure at the time of maximum pressure.

    Args:
        leak_off_curve: The leak off curve to query.
        maximum_pressure_sample: The sample (magnitude and time) of maximum pressure.

    Returns:

    """
    query_times = List[DateTime]()
    query_times.Add(maximum_pressure_sample.Timestamp)
    leak_off_pressure = leak_off_curve.GetPressureValues(query_times)[0]
    return leak_off_pressure


def calculate_maximum_pressure_sample(stage_part, ticks):
    """
    Calculate the sample (time stamp and magnitude) at which the maximum pressure occurs.

    Args:
        stage_part: The stage part used to limit the queried samples.
        ticks: A iterator of samples for the stage part.

    Returns:
        The sample (time stamp and magnitude) at which the maximum pressure occurs.
    """
    def maximum_pressure_reducer(so_far, candidate):
        if stage_part.StartTime <= candidate.Timestamp <= stage_part.StopTime and candidate.Value > so_far.Value:
            return candidate
        else:
            return so_far

    sentinel_maximum = object_factory.CreateTick[float](DateTime.MinValue, -1000)
    maximum_pressure_sample = functools.reduce(maximum_pressure_reducer, ticks, sentinel_maximum)
    return maximum_pressure_sample


def calculate_stage_part_pressure_samples(native_monitor, stage_part):
    """
    Calculate the pressure samples from the monitor for the `stage_part`.

    Args:
        native_monitor: The .NET `IMonitor` object recording pressures.
        stage_part: The .NET `IStagePart` limiting the monitor times to the stage treatment times.

    Returns:
        The pressure samples from `native_monitor` for the `stage_part`.
    """
    time_range = object_factory.CreateDateTimeOffsetRange(stage_part.StartTime.AddDays(-1),
                                                          stage_part.StopTime.AddDays(1))
    stage_part_pressure_samples = native_monitor.TimeSeries.GetOrderedTimeSeriesHistory(time_range)
    return stage_part_pressure_samples


def calculate_stage_part_visible_time_range(stage_part):
    """
    Calculate the visible time range of the stage treatment.

    Args:
        stage_part: The stage part identifying the stage treatment of interest.

    Returns:
        A `tuple` identifying the start and stop of the stage treatment.
    """
    return stage_part.StartTime.AddHours(-1), stage_part.StopTime.AddHours(1)


def create_leak_off_curve_control_points(leak_off_curve_times):
    """
    Create the control points for an observation.

    Args:
        leak_off_curve_times: The `dict` containing time stamps for specific leak off curve control points.

    Returns:
        The .NET `IList` containing the leak off curve control points.
    """
    leak_off_curve_control_points = List[DateTime]()
    leak_off_curve_control_points.Add(leak_off_curve_times['L1'])
    leak_off_curve_control_points.Add(leak_off_curve_times['L2'])
    return leak_off_curve_control_points


def auto_pick_observation_details(unpicked_observation, native_monitor, stage_part):
    """
    Change `unpicked_observation` by adding details to make it a picked observation.

    Args:
        unpicked_observation: The unpicked observation.
        native_monitor: The .NET `IMonitor` for this observation.
        stage_part: The .NET `IStagePart` observed by `native_monitor`.

    Returns:
        The "picked" observation with the appropriate details filled in.
    """
    # Auto pick observation details to be set
    # - Leak off curve type
    # - Control point times
    # - Visible range x-min time
    # - Visible range x-max time
    # - Position
    # - Delta pressure
    # - Notes
    # - Signal quality

    stage_part_pressure_samples = calculate_stage_part_pressure_samples(native_monitor, stage_part)

    leak_off_curve_times = {
        'L1': stage_part.StartTime.AddMinutes(-20),
        'L2': stage_part.StartTime,
    }
    control_point_times = calculate_leak_off_control_point_times(leak_off_curve_times['L1'],
                                                                 leak_off_curve_times['L2'],
                                                                 stage_part_pressure_samples)

    leak_off_curve = object_factory.CreateLeakoffCurve(Leakoff.LeakoffCurveType.Linear,
                                                       control_point_times)

    maximum_pressure_sample = calculate_maximum_pressure_sample(stage_part, stage_part_pressure_samples)
    leak_off_pressure = calculate_leak_off_pressure(leak_off_curve, maximum_pressure_sample)

    picked_observation = unpicked_observation  # An alias to better communicate intent
    with dnd.disposable(picked_observation.ToMutable()) as mutable_observation :
        mutable_observation.LeakoffCurveType = Leakoff.LeakoffCurveType.Linear
        mutable_observation.ControlPointTimes = create_leak_off_curve_control_points(leak_off_curve_times)
        (mutable_observation.VisibleRangeXminTime,
         mutable_observation.VisibleRangeXmaxTime) = calculate_stage_part_visible_time_range(stage_part)
        mutable_observation.Position = maximum_pressure_sample.Timestamp
        mutable_observation.DeltaPressure = calculate_delta_pressure(leak_off_pressure, maximum_pressure_sample)
        mutable_observation.Notes = "Auto-picked"
        mutable_observation.SignalQuality = Observation.SignalQualityValue.UndrainedCompressive

    return picked_observation


def auto_pick_observations(native_project, native_monitor):
    """
        Automatically pick observations for each treatment stage of `native_project` observed by `native_monitor`.
    Args:
        native_project: The `IProject` whose observations are sought.
        native_monitor: The `IMonitor` whose observations we automatically pick.

    Returns:

    """
    stage_parts = MonitorExtensions.FindPossiblyVisibleStageParts(native_monitor, native_project.Wells.Items)

    observation_set = object_factory.CreateObservationSet(native_project, 'Auto-picked Observation Set3')
    for part in stage_parts:
        # Create unpicked observation
        unpicked_observation = object_factory.CreateObservation(native_monitor, part)

        # Auto-pick observation details
        picked_observation = auto_pick_observation_details(unpicked_observation, native_monitor, part)

        # Add picked observation to observation set
        with dnd.disposable(observation_set.ToMutable()) as mutable_observation_set:
            mutable_observation_set.AddEvent(picked_observation)

    # TODO: Can we use Python disposable decorator?
    # Add observation set to project
    project_with_observation_set = native_project  # An alias to better communicate intent
    with dnd.disposable(native_project.ToMutable()) as mutable_project:
        mutable_project.AddObservationSet(observation_set)

    return project_with_observation_set


def main(cli_args):
    """
    Save project with automatically picked observations from original project read from disk.

    Args:
        cli_args: The command line arguments from `argparse.ArgumentParser`.
    """
    logging.basicConfig(level=logging.INFO)

    # Read Orchid project
    project = orchid.load_project(cli_args.input_project)
    native_project = project.dom_object

    # Automatically pick the observations for a specific monitor
    monitor_name = 'Demo_3H - MonitorWell'
    candidate_monitors = list(project.monitors().find_by_display_name(monitor_name))
    # I actually expect one or more monitors, but I only need one (arbitrarily the first one)
    assert len(candidate_monitors) > 0, (f'One or monitors with display name, "{monitor_name}", expected.'
                                         f' Found {len(candidate_monitors)}.')
    native_monitor = candidate_monitors[0].dom_object
    auto_pick_observations(native_project, native_monitor)

    # Log changed project data if requested
    if cli_args.verbosity >= 2:
        logging.info(f'{native_project.Name=}')
        logging.info(f'{len(native_project.ObservationSets.Items)=}')
        for observation_set in native_project.ObservationSets.Items:
            logging.info(f'{observation_set.Name=}')
            # TODO: Remove when >~ 2021.4
            # logging.info(f'{len(observation_set.LeakOffObservations.Items)=}')
            logging.info(f'{len(observation_set.GetObservations())=}')

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
        The project file name with a `.999` suffix inserted before the `.ifrac` suffix.
    """
    return ''.join([source_file_name.stem, '.999', source_file_name.suffix])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Automatically pick leak off observations.")
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

