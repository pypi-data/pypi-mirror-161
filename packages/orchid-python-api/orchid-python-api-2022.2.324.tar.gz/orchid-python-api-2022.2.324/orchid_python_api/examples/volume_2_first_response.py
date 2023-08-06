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
This notebook illustrates using the Orchid* Python API and the pandas package to
perform VFR analysis

(*Orchid is a mark of Reveal Energy Services, Inc)
"""

# Example: Using Pandas to Analyze Volume to First Response (VFR)

# 0.5 Import packages

# The only import needed for the Python API is `orchid` itself.

import orchid

# The remaining imports are standard python packages to support the analysis.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.signal as signal
import datetime as dt


# 1.0 Defining Support Functions

# Convenient constants

FIRST_DERIVATIVE_TIME = 'First Derivative Time'
SECOND_DERIVATIVE_TIME = 'Second Derivative Time'
V2FR_FIRST_DERIVATIVE = 'VFR (First Derivative)'
V2FR_SECOND_DERIVATIVE = 'VFR (Second Derivative)'
FIRST_DERIVATIVE_EVENT_TIME = 'First Derivative Event Time'
SECOND_DERIVATIVE_EVENT_TIME = 'Second Derivative Event Time'

# Completion Support Function

# This function will support taking in a stop time and calculating the treatment aggregates
def compute_stage_treatment_aggregates(treatment_stage, stop_time):
    # These calculations IGNORE all calculation warnings.
    pumped_fluid_volume = orchid.pumped_fluid_volume(treatment_stage,
                                                     treatment_stage.start_time,
                                                     stop_time)[0].magnitude
    total_proppant_mass = orchid.total_proppant_mass(treatment_stage,
                                                     treatment_stage.start_time,
                                                     stop_time)[0].magnitude
    median_treating_pressure = orchid.median_treating_pressure(treatment_stage,
                                                               treatment_stage.start_time,
                                                               stop_time)[0].magnitude
    return pumped_fluid_volume, total_proppant_mass, median_treating_pressure


# The first event-detection algorithm is to find when the first derivative exceeds a threshold value
def first_derivative_threshold(pressure_curve, threshold, window=51, poly=3):
    times = pressure_curve.index.values
    average_dt = np.mean(np.diff(pressure_curve.index)).total_seconds() / 60
    pressure = pressure_curve.values
    first_derivative = signal.savgol_filter(pressure,
                                            window_length=window,
                                            polyorder=poly,
                                            delta=average_dt,
                                            deriv=1)

    ndx = np.argwhere(first_derivative > threshold)

    return times[ndx[0][0]] if len(ndx) > 0 else None


# The second event-detection algorithm uses the second derivative which is fed into a peak finding algorithm
def second_derivative_peak(pressure_curve, window=51, poly=3):
    times = pressure_curve.index.values
    average_dt = np.mean(np.diff(pressure_curve.index)).total_seconds() / 60
    pressure = pressure_curve.values
    second_derivative = signal.savgol_filter(pressure,
                                             window_length=window,
                                             polyorder=poly,
                                             delta=average_dt,
                                             deriv=2)

    peaks = signal.find_peaks(second_derivative, height=0.2, distance=30, width=5)
    return times[peaks[0][0]] if len(peaks[0]) > 0 else None


def data_points_from_time_series_in_target_units(pressure_series, target_units):
    # ts is short variable name for data_points data
    ts_units = pressure_series.sampled_quantity_unit()
    ts = pressure_series.data_points()
    # Convert list of magnitudes (no units) to `numpy` array including units for faster operations
    ts_values_w_units = orchid.unit_registry.Quantity(ts.to_numpy(), ts_units.value[0])
    ts_in_target_units = ts_values_w_units.to(target_units.value[0])
    return pd.Series(data=ts_in_target_units.magnitude, index=ts.index)


def calculate_volume_2_first_response():
    # 2.0 Load the .ifrac project

    # The following code simply captures the configured location of the Orchid training data. It is not needed to
    # use the Orchid Python API itself, but it is used in this example to load well-known data.
    orchid_training_data_path = orchid.training_data_path()

    print('Wait patiently for the project to load...')
    permian_project = orchid.load_project(str(orchid_training_data_path.joinpath(
        'Project_frankNstein_Permian_UTM13_FEET.ifrac')))

    # 3.0 Extract Data and Apply Event Detectors

    # Takes a few minutes to run
    print('...And even more patiently for the calculations to complete...')
    p_time_series = list(permian_project.time_series().find_by_display_name('P1-Downhole-12550-Pressure'))
    p_time_series = p_time_series[0]  # Simply take the first matching time series
    p_data = data_points_from_time_series_in_target_units(p_time_series, orchid.unit_system.UsOilfield.PRESSURE)

    vfr_data = []
    for well in permian_project.wells().all_objects():
        for stage in well.stages().all_objects():
            stage_start_time = stage.start_time
            stage_stop_time = stage.stop_time

            # p_stg is the monitor pressure data with the given stage start/stop time
            p_stg = p_data[stage_start_time:stage_stop_time]
            derive_1_time = first_derivative_threshold(p_stg, 0.2)
            derive_2_time = second_derivative_peak(p_stg)
            if derive_1_time is not None:
                derive_1_time = dt.datetime.utcfromtimestamp(derive_1_time.tolist() * 1e-9).replace(tzinfo=orchid.UTC)
            if derive_2_time is not None:
                derive_2_time = dt.datetime.utcfromtimestamp(derive_2_time.tolist() * 1e-9).replace(tzinfo=orchid.UTC)
            vfr_d1, _, _ = (compute_stage_treatment_aggregates(stage, derive_1_time) if derive_1_time is not None
                            else (None, None, None))
            vfr_d2, _, _ = (compute_stage_treatment_aggregates(stage, derive_2_time) if derive_2_time is not None
                            else (None, None, None))
            vfr_data.append((well.name, stage.display_stage_number, derive_1_time, vfr_d1, derive_2_time, vfr_d2))

    # Show the dataframe
    df = pd.DataFrame(data=vfr_data, columns=['Well', 'Stage', FIRST_DERIVATIVE_TIME, V2FR_FIRST_DERIVATIVE,
                                              SECOND_DERIVATIVE_TIME, V2FR_SECOND_DERIVATIVE])
    print()
    print('Volume 2 First Response')
    print(df.to_string(max_rows=10))
    input('Press enter to continue...')

    # 3.1 Visualize the Pressure Data with Event Locations

    # Example with a selected well and stage number

    # Find a particularly interesting well and stage to visualize
    candidate_wells = list(permian_project.wells().find_by_display_name('C1'))
    well_0 = candidate_wells[0]
    selected_stage = well_0.stages().find_by_display_stage_number(8)

    p_stg = p_data[selected_stage.start_time:selected_stage.stop_time]
    plt.plot(p_stg, label='PData')
    ymin, ymax = plt.ylim()

    selected_ndx = 7  # Matches the DF index
    d1_x = df.iloc[selected_ndx][FIRST_DERIVATIVE_TIME]
    if d1_x is not None:
        plt.vlines(d1_x, ymin, ymax,  'r', label=FIRST_DERIVATIVE_EVENT_TIME)

    d2_x = df.iloc[selected_ndx][SECOND_DERIVATIVE_TIME]
    if d2_x is not None:
        plt.vlines(d2_x, ymin, ymax,  'k', label=SECOND_DERIVATIVE_EVENT_TIME)

    plt.legend()
    plt.xlabel('Time')
    plt.ylabel('Pressure')
    plt.title('VFR Analysis with Multiple Event Detectors')

    plt.show()


def main():
    print(__doc__)
    calculate_volume_2_first_response()


if __name__ == '__main__':
    main()
