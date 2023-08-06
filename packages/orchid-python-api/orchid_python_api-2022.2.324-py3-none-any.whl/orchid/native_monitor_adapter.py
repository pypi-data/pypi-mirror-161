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

import pendulum

import orchid.base
from orchid import (
    dot_net_dom_access as dna,
    dom_project_object as dpo,
    native_time_series_adapter as tsa,
    net_date_time as ndt,
)

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import IMonitor


class NativeMonitorAdapter(dpo.DomProjectObject):
    """Adapts a native IMonitor to python."""
    def __init__(self, net_monitor: IMonitor):
        """
        Constructs an instance adapting a .NET IMonitor.

        Args:
            net_monitor: The .NET monitor to be adapted.
        """
        super().__init__(net_monitor, orchid.base.constantly(net_monitor.Project))

    start_time = dna.transformed_dom_property('start_time', 'The start time of this monitor.',
                                              ndt.as_date_time)
    stop_time = dna.transformed_dom_property('stop_time', 'The stop time of this monitor.',
                                             ndt.as_date_time)
    well_time_series = dna.transformed_dom_property(
        'time_series',
        """The complete time series for the well that may be monitoring treatments.
        
        The returned time series contains all samples recorded for the project. More specifically, it may
        contain samples either before or after `time_range()`.
        
        Another consequence of this definition is that if a client wants to access sample inside 
        `time_range()`, one must write code to manually filter the series samples to only include the samples
        in `time_range()`.
        """,
        tsa.NativeTimeSeriesAdapter)

    @property
    def time_range(self):
        """
        Calculate the time range during which this monitor is active; that is, monitoring the treatment stage.

        Returns:
            The time range during which this monitor is active. The type of the returned value is
            `pendulum.Period`. See the [documentation](https://pendulum.eustace.io/docs/) to understand the
            methods available from a `pendulum.Period` instance.
        """
        return pendulum.Period(self.start_time, self.stop_time)
