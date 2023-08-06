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
This notebook illustrates using the Orchid* Python API and the `pandas` package to
search for and use project data frames.

(*Orchid is a mark of Reveal Energy Services, Inc)
"""

# Example: Searching for project data frames

# 0.5 Import packages

# The only import needed for the Orchid Python API is `orchid` itself.

import orchid

# The remaining imports are standard python packages to support the analysis.

import pprint
import uuid

import matplotlib.pyplot as plt
import pandas as pd
# The following import is included for its "side-effects" of an improved color schemes and
# plot styles. (See the "Tip" in section 9.2 of "Python for Data Analysis" for details.)
import seaborn as sns


def wait_for_input():
    input('Press enter to continue...')
    print()


def print_elided_data_frame(data_frame, title):
    print(title)
    print(data_frame.to_string(max_rows=10, max_cols=6))
    wait_for_input()


def search_data_frames():
    # 1.0 Load the .ifrac project

    # The following code simply captures the configured location of the Orchid training data. It is not needed to
    # use the Orchid Python API itself, but it is used in this example to load well-known data.

    orchid_training_data_path = orchid.training_data_path()

    print('Wait patiently for the project to load...')
    print()
    project = orchid.load_project(str(orchid_training_data_path.joinpath(
        'Project-frankNstein_Permian_UTM13FT_DF_PR2298_vs263.ifrac')))

    # 2.0 Search for a data frame using its object ID

    # I have copied to the object ID from Orchid itself.
    project_data_frame = project.data_frames().find_by_object_id(
        uuid.UUID('c08e6988-d8f5-4d7b-bccd-de968a5b398b'))
    if project_data_frame is not None:
        print_elided_data_frame(project_data_frame.pandas_data_frame(), 'Project Data Frame')

    # 3.0 Search for a data frame by its name

    fdi_data_frames = list(project.data_frames().find_by_name('FDI Observations'))
    assert(len(fdi_data_frames) == 1)
    fdi_data_frame = fdi_data_frames[0]
    print_elided_data_frame(fdi_data_frame.pandas_data_frame(), 'FDI Observations')

    # 4.0 Search for a data frame by its display name

    microseismic_data_frames = list(project.data_frames().find_by_display_name(
        'Microseismic Data Frame 01 (Potentially Corrupted)'))
    assert(len(microseismic_data_frames) == 1)
    microseismic_data_frame = microseismic_data_frames[0]
    print_elided_data_frame(microseismic_data_frame.pandas_data_frame(), 'Microseismic Data Frame')

    # 5.0 Query for all identifying information

    print('All data frame object IDs')
    pprint.pprint(list(project.data_frames().all_object_ids()))
    wait_for_input()

    print('All data frame names')
    pprint.pprint(list(project.data_frames().all_names()))
    wait_for_input()

    print('All data frame display names')
    pprint.pprint(list(project.data_frames().all_display_names()))
    wait_for_input()

    # 7.0 Leverage the full power of pandas

    stage_12_data_frame = project.data_frames().find_by_object_id(
        uuid.UUID('5304d2ac-dbf8-44db-8dd8-c2203714c456'))
    print_elided_data_frame(stage_12_data_frame.pandas_data_frame(), 'Stage 12 Data Frame')

    # Extract a specific column (the cumulative slurry of a stage)

    print('Cumulative Slurry (bbl)')
    print(stage_12_data_frame.pandas_data_frame()[' cum slurry [bll]'].to_string(max_rows=10))
    wait_for_input()

    # Find the maximum value (the volume to pick from the FDI data frame)

    print('Maximum Volume to Pick')
    print(max(fdi_data_frame.pandas_data_frame()['VolumeToPick']))
    wait_for_input()

    # 7.1 Summarize the completion data

    raw_completion_column_names = ['Timestamp', 'DeltaT', 'DeltaP', 'VolumeToPick', 'ProppantMass', 'Energy']

    # Extract completion columns into new data frame and change index to time
    raw_completion_details = fdi_data_frame.pandas_data_frame()[
        raw_completion_column_names].set_index('Timestamp')

    raw_completion_details.describe()

    # 7.2 Scale completion data to fit on single plot

    def scale_down_by_1000(v):
        return v / 1000.0

    copy_completion_details = raw_completion_details.copy()
    copy_completion_details['ProppantMass'] = copy_completion_details['ProppantMass'].transform(scale_down_by_1000)
    copy_completion_details['Energy'] = copy_completion_details['Energy'].transform(scale_down_by_1000)
    copy_completion_details['VolumeToPick'] = copy_completion_details['VolumeToPick'].transform(scale_down_by_1000)

    completion_details = copy_completion_details.rename({'ProppantMass': 'ProppantMass (1000 lbs)',
                                                         'Energy': 'Energy (1000 ft-lb)',
                                                         'VolumeToPick': 'VolumeToPick (Mbbl)'},
                                                        axis='columns', errors='raise')
    print_elided_data_frame(completion_details, 'Completion Data')

    # 7.3 Plot the completion data

    _axes = completion_details.plot(figsize=(8, 5), title='Completion Data')
    plt.show()


def main():
    print(__doc__)
    search_data_frames()


if __name__ == '__main__':
    main()
