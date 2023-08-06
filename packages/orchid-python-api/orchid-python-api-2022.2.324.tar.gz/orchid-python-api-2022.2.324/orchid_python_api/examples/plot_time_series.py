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
This script illustrates using the Orchid* Python API and `matplotlib` to plot well time series.

(*Orchid is a mark of Reveal Energy Services, Inc)
"""

# Example: Plotting well time series

# 0.5 Import packages

# The only import needed for the Python API is `orchid` itself.

import orchid

# The remaining imports are standard python packages to support the analysis.

import numpy as np
import matplotlib.pyplot as plt
# The following import is included for its "side-effects" of an improved color schemes and
# plot styles. (See the "Tip" in section 9.2 of "Python for Data Analysis" for details.)
import seaborn as sns


def plot_single_time_series(using_series, on_axes, using_color, physical_quantity,
                            unit_abbreviation, name):
    """
    Plot the specified time series using the supplied details

    Args:
        using_series: The series to plot.
        on_axes: The axes on which to plot the series.
        using_color: The color for the plot.
        physical_quantity: The physical quantity of the series.
        unit_abbreviation: The abbreviation of the unit_abbreviation of the plotted samples.
        name: The name of the curve.
    """
    using_series.plot(ax=on_axes, color=using_color)
    on_axes.set_ylabel(f'{str(physical_quantity).title()} ({unit_abbreviation})')
    on_axes.title.set_text(name)
    x_tick_labels = on_axes.get_xticklabels()
    plt.setp(x_tick_labels, rotation=30)


def plot_time_series():
    """Plot a number of time series for a project."""

    # The following code simply captures the configured location of the Orchid training data. It is not needed to
    # use the Orchid Python API itself, but it is used in this example to load well-known data.

    orchid_training_data_path = orchid.training_data_path()

    # 1.0 Load the .ifrac project

    project = orchid.load_project(str(orchid_training_data_path.joinpath(
        'Project_frankNstein_Permian_UTM13_FEET.ifrac')))

    # 1.1 Get the time series (be patient)

    all_time_series = list(project.time_series().all_objects())
    all_time_series_display_names = list(project.time_series().all_display_names())
    data_points = [series.data_points() for series in all_time_series]

    # 1.2 Plot the time series in a 4x4 array

    default_well_colors = ['#%02x%02x%02x' % tuple(map(lambda c: int(255 * c), (r, g, b)))
                           for (r, g, b) in project.default_well_colors()]
    plot_series_shape = (2, 2)
    max_curve_count = plot_series_shape[0] * plot_series_shape[1]
    figure, axes = plt.subplots(*plot_series_shape, figsize=(16, 9), dpi=72)
    figure.subplots_adjust(hspace=0.5)
    time_series_to_plot = np.reshape(all_time_series[:max_curve_count], plot_series_shape)
    data_points_to_plot = np.reshape(np.array(data_points[:max_curve_count], dtype=object), plot_series_shape)
    names_to_display = np.reshape(all_time_series_display_names[:max_curve_count], plot_series_shape)
    colors_to_use = np.reshape(default_well_colors[:max_curve_count], plot_series_shape)
    for i in range(len(axes)):
        for j in range(len(axes[0])):
            series = time_series_to_plot[i, j]
            points = data_points_to_plot[i, j]
            ax = axes[i, j]
            color = colors_to_use[i, j]
            quantity_name = series.sampled_quantity_name
            abbreviation = orchid.abbreviation(series.sampled_quantity_unit())
            series_name = names_to_display[i, j]
            plot_single_time_series(points, ax, color, quantity_name, abbreviation, series_name)

    plt.show()


def main():
    print(__doc__)
    print('Be very patient.')
    plot_time_series()


if __name__ == '__main__':
    main()
