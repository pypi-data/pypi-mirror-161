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
This script illustrates using the Orchid* Python API and the `matplotlib` package to plot well trajectories.

(*Orchid is a mark of Reveal Energy Services, Inc)
"""


# Example: Plotting well trajectories

# 0.5 Import packages

# The only import needed for the Orchid Python API is `orchid` itself.
import orchid

# The remaining imports are standard python packages to support the analysis.

import matplotlib.pyplot as plt
# The following import is included for its "side-effects" of an improved color schemes and
# plot styles. (See the "Tip" in section 9.2 of "Python for Data Analysis" for details.)
import seaborn as sns


def plot_trajectories():
    """Plot the trajectories for a single well."""

    # The following code simply captures the configured location of the Orchid training data. It is not needed to
    # use the Orchid Python API itself, but it is used in this example to load well-known data.
    orchid_training_data_path = orchid.training_data_path()

    # 1.0 Load the .ifrac project

    project = orchid.load_project(str(orchid_training_data_path.joinpath(
        'Project-frankNstein_Montney_UTM13_METERS.ifrac')))

    # 1.1 Get the trajectories for each well of the project

    all_wells = project.wells().all_objects()
    wells = dict([(w.name, w) for w in all_wells])
    trajectories = {wn: w.trajectory for (wn, w) in wells.items()}

    # 1.2 Get the eastings ond northings in the project reference frame

    eastings = {wn: t.get_easting_array(orchid.WellReferenceFrameXy.PROJECT) for (wn, t) in trajectories.items()}
    northings = {wn: t.get_northing_array(orchid.WellReferenceFrameXy.PROJECT) for (wn, t) in trajectories.items()}

    # 2.0 Plot the eastings and northings for each trajectory

    default_well_colors = project.default_well_colors()
    for (i, wn) in enumerate(wells.keys()):
        plt.plot(eastings[wn], northings[wn],
                 label=f'{wells[wn].display_name}',
                 color=default_well_colors[i % len(default_well_colors)])
    plt.title(f'{project.name} Well Trajectories (Project Coordinates)')
    plt.legend(loc='best')
    plt.xlabel(f'Easting ({orchid.abbreviation(project.project_units.LENGTH)})')
    plt.ylabel(f'Northing ({orchid.abbreviation(project.project_units.LENGTH)})')

    plt.rcParams['figure.dpi'] = 150
    plt.show()


def main():
    print(__doc__)
    plot_trajectories()


if __name__ == '__main__':
    main()
