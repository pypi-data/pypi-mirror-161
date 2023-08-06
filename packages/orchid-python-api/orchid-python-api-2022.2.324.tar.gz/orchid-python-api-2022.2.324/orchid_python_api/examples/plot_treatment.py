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
This script illustrates using the Orchid* Python API, `matplotlib` and `pandas` to
plot the treatment curves (treating pressure, slurry rate and proppant concentration)
for a single stage.

(*Orchid is a mark of Reveal Energy Services, Inc)
"""

# Example: Plotting treatment curves for a stage

# 0.5 Import packages

# The only import needed for the Python API is `orchid` itself.

import orchid

# The remaining imports are standard python packages to support the analysis.

import pandas as pd
import matplotlib.pyplot as plt
# The following import is included for its "side-effects" of an improved color schemes and
# plot styles. (See the "Tip" in section 9.2 of "Python for Data Analysis" for details.)
import seaborn as sns


def plot_treatment():
    """
    Plot a treatment curves for a single stage of a well
    """

    # The following code simply captures the configured location of the Orchid training data. It is not needed to
    # use the Orchid Python API itself, but it is used in this example to load well-known data.
    orchid_training_data_path = orchid.training_data_path()

    # 1.0 Load the .ifrac project
    project = orchid.load_project(str(orchid_training_data_path.joinpath(
        'frankNstein_Bakken_UTM13_FEET.ifrac')))

    # 1.1 Get the treatment curves for the stage of interest

    well_name = 'Demo_2H'
    candidate_wells = list(project.wells().find_by_name(well_name))
    assert len(candidate_wells) == 1
    well = candidate_wells[0]

    stage_no = 39
    stage = well.stages().find_by_display_stage_number(stage_no)

    curves = stage.treatment_curves()
    curve_names = [orchid.TreatmentCurveTypes.TREATING_PRESSURE,
                   orchid.TreatmentCurveTypes.SLURRY_RATE,
                   orchid.TreatmentCurveTypes.SURFACE_PROPPANT_CONCENTRATION]
    treatment_series = [curves[n].data_points() for n in curve_names]
    treatment_curves = pd.concat(treatment_series, axis=1)
    treatment_curves.columns = [
        f'{orchid.TreatmentCurveTypes.TREATING_PRESSURE.value} ({orchid.abbreviation(project.project_units.PRESSURE)})',
        f'{orchid.TreatmentCurveTypes.SLURRY_RATE.value} ({orchid.abbreviation(project.project_units.SLURRY_RATE)})',
        f'{orchid.TreatmentCurveTypes.SURFACE_PROPPANT_CONCENTRATION.value}'
        f' ({orchid.abbreviation(project.project_units.PROPPANT_CONCENTRATION)})'
    ]

    title = f'Treatment Curves: Stage {stage_no} of Well {well_name}'
    print(title)
    print(treatment_curves.to_string(max_rows=10))

    # 1.2 Plot the three treatment curves

    axes = treatment_curves.plot(subplots=True,
                                 title=f'Treatment Curves: Stage {stage_no} of Well {well_name}')

    axes[0].set_ylabel(f'{orchid.abbreviation(project.project_units.PRESSURE)}')
    axes[1].set_ylabel(f'{orchid.abbreviation(project.project_units.SLURRY_RATE)}')
    axes[2].set_ylabel(f'{orchid.abbreviation(project.project_units.PROPPANT_CONCENTRATION)}')

    plt.rcParams['figure.dpi'] = 150
    plt.show()


def main():
    print(__doc__)
    plot_treatment()


if __name__ == '__main__':
    main()
