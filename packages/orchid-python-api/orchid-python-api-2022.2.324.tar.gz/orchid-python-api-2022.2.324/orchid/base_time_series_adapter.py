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


from abc import ABCMeta, abstractmethod
from typing import Callable, Union

import numpy as np
import pandas as pd

from orchid import (
    dom_project_object as dpo,
    dot_net_dom_access as dna,
    project_store as loader,
    unit_system as units,
)

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.SDKFacade import ScriptAdapter
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.TimeSeries import IQuantityTimeSeries


class BaseTimeSeriesAdapter(dpo.DomProjectObject, metaclass=ABCMeta):
    def __init__(self, adaptee: IQuantityTimeSeries, net_project_callable: Callable):
        """
        Construct an instance that adapts a .NET `IStageSampledQuantityTimeSeries` instance.

        Args:
            adaptee: The .NET stage time series to be adapted.
        """
        super().__init__(adaptee, net_project_callable)

    sampled_quantity_name = dna.dom_property('sampled_quantity_name',
                                             'Return the sampled quantity name for this curve.')

    @abstractmethod
    def quantity_name_unit_map(self, project_units):
        """
        Return a map (dictionary) between quantity names and units (from `unit_system`) of the data_points.

        This method plays the role of "Primitive Operation" in the *Template Method* design pattern. In this
        role, the "Template Method" defines an algorithm and delegates some steps of the algorithm to derived
        classes through invocation of "Primitive Operations".

        Args:
            project_units: The unit system of the project.
        """
        pass

    def sampled_quantity_unit(self) -> Union[units.UsOilfield, units.Metric]:
        """
        Return the measurement unit of the data_points in this curve.

        This method plays the role of "Template Method" in the *Template Method* design pattern. In this role
        it specifies an algorithm to calculate the units of the sampled quantity of the curve delegating some
        algorithm steps to derived classes by invoking the "Primitive Operation-", `quantity_name_unit_map()`
        and `get_net_project_units()`.

        Returns:
            A `UnitSystem` member containing the unit for the sample in this curve.
        """
        quantity_name_unit_map = self.quantity_name_unit_map(self.expect_project_units)
        return quantity_name_unit_map[self.sampled_quantity_name]

    def data_points(self) -> pd.Series:
        """
        Return the time series for this curve.

        Returns
            The `pandas` time `Series` for this curve.
        """
        python_time_series_arrays = loader.as_python_time_series_arrays(self.dom_object)

        result = pd.Series(data=np.fromiter(python_time_series_arrays.SampleMagnitudes, dtype='float'),
                           index=pd.DatetimeIndex(np.fromiter(python_time_series_arrays.UnixTimeStampsInSeconds,
                                                              dtype='datetime64[s]'), tz='UTC'),
                           name=self.name)

        return result
