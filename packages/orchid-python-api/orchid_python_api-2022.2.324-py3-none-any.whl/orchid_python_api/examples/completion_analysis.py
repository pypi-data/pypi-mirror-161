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
This script illustrates using the Orchid* Python API, `pandas` and `matplotlib` to perform completion
 analysis.

(*Orchid is a mark of Reveal Energy Services, Inc)
"""

# Example: Using Pandas to Analyze Completion Parameters

# %% md

# 0.5 Import packages

# The only import needed for the Python API is `orchid` itself.

import orchid

# The remaining imports are standard python packages to support the analysis.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
# The following import is included for its "side effects" of an improved color schemes and
# plot styles. (See the "Tip" in section 9.2 of "Python for Data Analysis" for details.)
import seaborn as sns


def compute_stage_treatment_aggregates(treatment_stage):
    """
    Compute the aggregate stage treatment data.

    Args:
        treatment_stage: The treatment stage whose aggregate data is sought.

    Returns:
        A `tuple` containing the treatment stage aggregate data.
    """

    # These calculations IGNORE all calculation warnings.
    pumped_fluid_volume = orchid.pumped_fluid_volume(treatment_stage,
                                                     treatment_stage.start_time,
                                                     treatment_stage.stop_time)[0].magnitude
    total_proppant_mass = orchid.total_proppant_mass(treatment_stage,
                                                     treatment_stage.start_time,
                                                     treatment_stage.stop_time)[0].magnitude
    median_treating_pressure = orchid.median_treating_pressure(treatment_stage,
                                                               treatment_stage.start_time,
                                                               treatment_stage.stop_time)[0].magnitude
    return pumped_fluid_volume, total_proppant_mass, median_treating_pressure


def show_proppant_loading_plot(data_frame, columns):
    """
    Build a proppant loading plot from `columns` of `data_frame`.

    Args:
        data_frame: Contains the data used to create the plot.
        columns: The columns containing the data to plot.
    """
    groups = data_frame.groupby(columns['well'])

    fig, ax = plt.subplots(len(groups), sharex='all', sharey='all', dpi=150)
    fig.suptitle(f'{columns["proppant_loading"]} by Stage')
    i = 0
    colors = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple',
              'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']
    for name, group in groups:
        ax[i].margins(0.05)  # Optional, just adds 5% padding to the autoscaling
        ax[i].plot(group[columns['stage']],
                   group[columns['proppant_loading']],
                   colors[i], marker='o', linestyle='', ms=6, label=name)
        ax[i].legend()
        ax[i].set_xlabel('Stage Number')
        i = i + 1
        # Hide x labels and tick labels for all but bottom plot.
    for a in ax:
        a.label_outer()
    plt.rcParams['figure.dpi'] = 150
    plt.show()


def to_unit(magnitude, src_unit, tgt_unit):
    """
    Helper function to convert units.

    Args:
        magnitude: The magnitude of the source.
        src_unit: The unit of measurement of the source.
        tgt_unit: The unit of measurement of the target.

    Returns:
        The magnitude of the source measurement measured in `tgt_unit`.
    """
    src_measurement = orchid.make_measurement(src_unit, magnitude)
    tgt_measurement = orchid.to_unit(tgt_unit, src_measurement)
    result = tgt_measurement.magnitude
    return result


def print_elided_data_frame(data_frame, title):
    print(title)
    print(data_frame.to_string(max_rows=10, max_cols=6))
    input('Press enter to continue...')
    print()


def analyze_completions():
    # 1.0 Load the .ifrac project

    # The following code simply captures the configured location of the Orchid training data. It is not needed
    # to use the Orchid Python API itself, but it is used in this example to load well - known data.
    orchid_training_data_path = orchid.training_data_path()

    bakken_project = orchid.load_project(str(orchid_training_data_path.joinpath(
        'frankNstein_Bakken_UTM13_FEET.ifrac')))

    # 3.0 Build a pandas data frame

    # Remember the project units
    bakken_units = bakken_project.project_units

    # Calculate the stage results
    stage_results = []
    for well in bakken_project.wells().all_objects():

        for stage in well.stages().all_objects():

            treatment_aggregates = compute_stage_treatment_aggregates(stage)
            # Skip stages with no aggregates. These stages most likely are from
            # an untreated monitor well.
            if not treatment_aggregates:
                continue

            stage_fluid, stage_proppant, median_stage_pressure = treatment_aggregates
            stage_results.append((bakken_project.name, well.name, stage.display_stage_number,
                                  stage.md_top(bakken_units.LENGTH).magnitude,
                                  stage.md_bottom(bakken_units.LENGTH).magnitude,
                                  stage_fluid, stage_proppant, median_stage_pressure))

    # Provide a way to manage DataFrame column names (which include units) using simpler,
    # semantic identifiers. Creating the column names helps me avoid "typos" involved in
    # getting the (project-specific) units correct, but is not necessary in a typical
    # interactive session.

    bakken_columns = {'project': 'Project',
                      'well': 'Well',
                      'stage': 'Stage',
                      'md_top': f'MD Top ({orchid.abbreviation(bakken_units.LENGTH)})',
                      'md_bottom': f'MD Bottom ({orchid.abbreviation(bakken_units.LENGTH)})',
                      'total_fluid':
                          f'Total Fluid ({orchid.abbreviation(bakken_project.slurry_rate_volume_unit())})',
                      'total_proppant':
                          f'Total Proppant ({orchid.abbreviation(bakken_project.proppant_concentration_mass_unit())})',
                      'median_treating':
                          f'Median Treating Pressure ({orchid.abbreviation(bakken_units.PRESSURE)})'}

    # Create the data frame
    bakken_summaries = pd.DataFrame(data=stage_results, columns=bakken_columns.values())
    print_elided_data_frame(bakken_summaries, 'Initial Bakken summaries data frame')

    # 3.1 Compute the stage length directly from the summary

    bakken_summaries[f'Stage Length ({orchid.abbreviation(bakken_units.LENGTH)})'] = \
        bakken_summaries.apply(lambda s: s[bakken_columns['md_bottom']] - s[bakken_columns['md_top']], axis=1)
    bakken_columns['stage_length'] = bakken_summaries.columns[-1]
    print_elided_data_frame(bakken_summaries, 'Bakken summaries with stage lengths')

    # 3.2 Now compute the proppant loading for each stage

    bakken_summaries[f'Proppant loading' \
                     f' ({orchid.abbreviation(bakken_project.proppant_concentration_mass_unit())}/'
                     f'{orchid.abbreviation(bakken_units.LENGTH)})'] = \
        bakken_summaries.apply(lambda s: s[bakken_columns['total_proppant']] / s[bakken_columns['stage_length']],
                               axis=1)
    bakken_columns['proppant_loading'] = bakken_summaries.columns[-1]
    print_elided_data_frame(bakken_summaries, 'Bakken summaries with proppant loading')

    # 4.0 Completion questions

    # 4.1 What is the median proppant intensity per well?

    bakken_summaries[[bakken_columns['well'],
                      bakken_columns['proppant_loading']]].groupby(bakken_columns['well']).median()

    groups = bakken_summaries.groupby(bakken_columns['well'])

    fig, ax = plt.subplots(dpi=150)
    ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling
    for name, group in groups:
        ax.plot(group[bakken_columns['stage']], group[bakken_columns['proppant_loading']],
                marker='o', linestyle='', ms=6, label=name)
    ax.legend()
    plt.show()

    # That's a little hard to interpret with the outliers

    # Plot
    groups = bakken_summaries[bakken_summaries[bakken_columns['stage']] > 5].groupby(bakken_columns['well'])

    fig, ax = plt.subplots(dpi=150)
    ax.margins(0.05)  # Optional, just adds 5% padding to the autoscaling
    for name, group in groups:
        ax.plot(group[bakken_columns['stage']], group[bakken_columns['proppant_loading']],
                marker='o', linestyle='', ms=6, label=name)
    ax.legend()
    ax.set_title(f'Proppant Loading by Stage')
    ax.set_xlabel('Stage Number')
    ax.set_ylabel(bakken_columns['proppant_loading'])
    plt.show()

    # That's a little busy. Let' s clean it up.

    show_proppant_loading_plot(bakken_summaries[bakken_summaries[bakken_columns['stage']] > 5], bakken_columns)

    # 4.2 What is the median treating pressure per well?

    bakken_summaries[[bakken_columns['well'],
                      bakken_columns['median_treating']]].groupby(bakken_columns['well']).median()

    groups = bakken_summaries.groupby(bakken_columns['well'])

    fig, ax = plt.subplots(3, sharex='all', sharey='all', dpi=150)
    fig.suptitle(f'{bakken_columns["median_treating"]} by Stage')
    i = 0
    colors = ['tab:blue', 'tab:orange', 'tab:green',
              'tab:purple', 'tab:yellow', 'tab:red', 'tab:black']
    for name, group in groups:
        ax[i].margins(0.05)
        ax[i].plot(group[bakken_columns['stage']],
                   group[bakken_columns['median_treating']],
                   colors[i], marker='o', linestyle='', ms=6, label=name)
        ax[i].legend()
        ax[i].set_xlabel('Stage Number')
        i = i + 1

        # Hide x labels and tick labels for all but bottom plot.
    for a in ax:
        a.label_outer()
    plt.show()

    # 5.0 Add another .ifrac project

    print('Wait patiently while I add another project...')
    print()

    montney_project = orchid.load_project(str(orchid_training_data_path.joinpath(
        'Project-frankNstein_Montney_UTM13_METERS.ifrac')))

    montney_units = montney_project.project_units

    # Calculate the stage results for the Montney project
    stage_results = []
    for well in montney_project.wells().all_objects():

        for stage in well.stages().all_objects():

            treatment_aggregates = compute_stage_treatment_aggregates(stage)
            # Skip stages with no aggregates. These stages most likely are from
            # an untreated monitor well.
            if not treatment_aggregates:
                continue

            stage_fluid, stage_proppant, median_stage_pressure = treatment_aggregates
            stage_results.append((montney_project.name, well.name, stage.display_stage_number,
                                  stage.md_top(montney_units.LENGTH).magnitude,
                                  stage.md_bottom(montney_units.LENGTH).magnitude,
                                  stage_fluid, stage_proppant, median_stage_pressure))

    # Provide a way to manage DataFrame column names (which include units) using simpler,
    # semantic identifiers.
    montney_columns = {'project': 'Project',
                       'well': 'Well',
                       'stage': 'Stage',
                       'md_top': f'MD Top ({orchid.abbreviation(montney_units.LENGTH)})',
                       'md_bottom': f'MD Bottom ({orchid.abbreviation(montney_units.LENGTH)})',
                       'total_fluid':
                           f'Total Fluid ('
                           f'{orchid.abbreviation(montney_project.slurry_rate_volume_unit())})',
                       'total_proppant':
                           f'Total Proppant ('
                           f'{orchid.abbreviation(montney_project.proppant_concentration_mass_unit())})',
                       'median_treating':
                           f'Median Treating Pressure ({orchid.abbreviation(montney_units.PRESSURE)})'}

    # Create the Montney data frame
    montney_summaries = pd.DataFrame(data=stage_results, columns=montney_columns.values())

    montney_summaries[f'Stage Length ({orchid.abbreviation(montney_units.LENGTH)})'] = \
        montney_summaries.apply(lambda s: s[montney_columns['md_bottom']] - s[montney_columns['md_top']], axis=1)
    montney_columns['stage_length'] = montney_summaries.columns[-1]

    montney_summaries[f'Proppant loading'
                      f' ({orchid.abbreviation(montney_project.proppant_concentration_mass_unit())}/'
                      f'{orchid.abbreviation(montney_units.LENGTH)})'] = \
        montney_summaries.apply(lambda s: s[montney_columns['total_proppant']] / s[montney_columns['stage_length']],
                                axis=1)
    montney_columns['proppant_loading'] = montney_summaries.columns[-1]

    print_elided_data_frame(montney_summaries, 'Montney summaries')

    # 5.1 Combine the data for the two projects.

    # The frankNstein_Bakken_UTM13_FEET project is in US Oilfield units, and the
    # "Project - frankNstein_Montney_UTM13_METERS" project is in metric units. I need to convert one to the other.

    # Calculate the stage results in US oilfield units for the Montney project
    stage_results = []
    for well in montney_project.wells().all_objects():

        for stage in well.stages().all_objects():

            treatment_aggregates = compute_stage_treatment_aggregates(stage)
            if not treatment_aggregates:
                continue

            # Convert stage aggregates to US oilfield units
            stage_fluid = to_unit(treatment_aggregates[0], montney_project.slurry_rate_volume_unit(),
                                  bakken_project.slurry_rate_volume_unit())
            stage_proppant = to_unit(treatment_aggregates[1], montney_project.proppant_concentration_mass_unit(),
                                     bakken_project.proppant_concentration_mass_unit())
            median_stage_pressure = to_unit(treatment_aggregates[2], montney_units.PRESSURE, bakken_units.PRESSURE)

            # Append results for this stage
            stage_results.append((montney_project.name, well.name,
                                  stage.display_stage_number,
                                  stage.md_top(bakken_units.LENGTH).magnitude,
                                  stage.md_bottom(bakken_units.LENGTH).magnitude,
                                  stage_fluid, stage_proppant, median_stage_pressure))

    # Create the converted Montney data frame
    montney_us_summaries = pd.DataFrame(data=stage_results,
                                        columns=list(bakken_columns.values())[:-2])

    montney_us_summaries[f'Stage Length ({orchid.abbreviation(bakken_units.LENGTH)})'] = \
        montney_us_summaries.apply(lambda s: s[bakken_columns['md_bottom']] - s[bakken_columns['md_top']], axis=1)

    montney_us_summaries[f'Proppant loading' 
                         f' ({orchid.abbreviation(bakken_project.proppant_concentration_mass_unit())}/'
                         f'{orchid.abbreviation(bakken_units.LENGTH)})'] = \
        montney_us_summaries.apply(lambda s: s[bakken_columns['total_proppant']] / s[bakken_columns['stage_length']],
                                   axis=1)

    print_elided_data_frame(montney_us_summaries, 'Montney summaries in US Oilfield units')

    combined = pd.concat([bakken_summaries[bakken_summaries[bakken_columns['stage']] > 5], montney_us_summaries])
    print_elided_data_frame(combined, 'Combined Bakken and Montney summaries')

    combined[[bakken_columns['well'],
              bakken_columns['proppant_loading']]].groupby(bakken_columns['well']).median()

    combined[[bakken_columns['well'],
              bakken_columns['proppant_loading']]] \
        .groupby(bakken_columns['well']) \
        .agg({bakken_columns['proppant_loading']: ['median', 'std']})

    show_proppant_loading_plot(combined, bakken_columns)


def main():
    print(__doc__)
    analyze_completions()


if __name__ == '__main__':
    main()
