#  Copyright (c) 2017-2022 Reveal Energy Services, Inc 
#
#  Licensed under the Apache License, Version 2.0 (the "License"); 
#  you may not use this file except in compliance with the License. 
#  You may obtain a copy of the License at 
#
#      http://www.apache.org/licenses/LICENSE-2.0 
#
#  Unless required by applicable law or agreed to in writing, software 
#  distributed under the License is distributed on an "AS IS" BASIS, 
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. 
#  See the License for the specific language governing permissions and 
#  limitations under the License. 
#
# This file is part of Orchid and related technologies.
#

from collections import namedtuple
from typing import Iterable, List, Tuple

import deal
import option
import toolz.curried as toolz

from orchid import (
    dot_net_dom_access as dna,
    searchable_project_objects as spo,
    native_data_frame_adapter as dfa,
    native_monitor_adapter as nma,
    native_time_series_adapter as tsa,
    native_project_user_data_adapter as uda,
    native_well_adapter as nwa,
    net_quantity as onq,
    unit_system as units,
)
from orchid.project_store import ProjectStore

# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics import IWell, UnitSystem
# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics.Settings import IProjectUserData
# noinspection PyUnresolvedReferences
import UnitsNet


ProjectBounds = namedtuple('ProjectBounds', [
    'min_x', 'max_x',
    'min_y', 'max_y',
    'min_depth', 'max_depth',
])
SurfacePoint = namedtuple('SurfacePoint', ['x', 'y'])


class Project(dna.IdentifiedDotNetAdapter):
    """Adapts a .NET `IProject` to a Pythonic interface."""

    @deal.pre(lambda self, project_loader: project_loader is not None)
    def __init__(self, project_loader: ProjectStore):
        """
        Construct an instance adapting he project available from net_project.

        :param project_loader: Loads an IProject to be adapted.
        """
        super().__init__(project_loader.native_project())
        self._project_loader = project_loader

    azimuth = dna.transformed_dom_property('azimuth', 'The azimuth of the project measured east of north.',
                                           toolz.compose(onq.as_measurement(units.Common.ANGLE),
                                                         option.maybe))
    name = dna.dom_property('name', 'The name of this project.')
    project_units = dna.transformed_dom_property('project_units', 'The project unit system.', units.as_unit_system)

    # _data_frames = dna.map_reduce_dom_property('data_frames', 'The project data frames.',
    #                                            dfa.NativeDataFrameAdapterIdentified, dna.dictionary_by_id, {})

    @property
    def fluid_density(self):
        """The fluid density of the project in project units."""
        return onq.as_measurement(self.project_units.DENSITY, option.maybe(self.dom_object.FluidDensity))

    def data_frames(self) -> spo.SearchableProjectObjects:
        """
        Return a `spo.SearchableProjectObjects` instance of all the data frames for this project.

        Returns:
            An `spo.SearchableProjectObjects` for all the data frames of this project.
        """
        return spo.SearchableProjectObjects(dfa.NativeDataFrameAdapterIdentified, self.dom_object.DataFrames.Items)

    def default_well_colors(self) -> List[Tuple[float, float, float]]:
        """
        Calculate the default well colors for this project.
        :return: A list of RGB tuples.
        """
        result = list(map(tuple, self._project_loader.native_project().PlottingSettings.GetDefaultWellColors()))
        return result

    def monitors(self) -> spo.SearchableProjectObjects:
        """
        Return a `spo.SearchableProjectObjects` instance of all the monitors for this project.

        Returns:
            An `spo.SearchableProjectObjects` for all the monitors of this project.
        """
        return spo.SearchableProjectObjects(nma.NativeMonitorAdapter, self.dom_object.Monitors.Items)

    def project_bounds(self) -> ProjectBounds:
        result = toolz.pipe(self.dom_object.GetProjectBounds(),
                            toolz.map(option.maybe),
                            toolz.map(onq.as_measurement(self.project_units.LENGTH)),
                            list,
                            lambda ls: ProjectBounds(*ls))
        return result

    def project_center(self) -> SurfacePoint:
        """
        Return the location of the project center on the surface measured in project units.
        """
        net_center = self.dom_object.GetProjectCenter()
        result = toolz.pipe(net_center,
                            toolz.map(option.maybe),
                            toolz.map(onq.as_measurement(self.project_units.LENGTH)),
                            list,
                            lambda ls: SurfacePoint(ls[0], ls[1]))
        return result

    def proppant_concentration_mass_unit(self):
        if self.project_units == units.UsOilfield:
            return units.UsOilfield.MASS
        elif self.project_units == units.Metric:
            return units.Metric.MASS
        else:
            raise ValueError(f'Unknown unit system: {self.project_units}')

    def slurry_rate_volume_unit(self):
        if self.project_units == units.UsOilfield:
            return units.UsOilfield.VOLUME
        elif self.project_units == units.Metric:
            return units.Metric.VOLUME
        else:
            raise ValueError(f'Unknown unit system: {self.project_units}')

    def time_series(self) -> spo.SearchableProjectObjects:
        """
        Return a `spo.SearchableProjectObjects` instance of all the time series for this project.

        Returns:
            An `spo.SearchableProjectObjects` for all the time series of this project.
        """
        return spo.SearchableProjectObjects(tsa.NativeTimeSeriesAdapter, self.dom_object.WellTimeSeriesList.Items)

    @property
    def user_data(self) -> uda.NativeProjectUserDataAdapter:
        return uda.NativeProjectUserDataAdapter(self.dom_object.ProjectUserData)

    def wells(self) -> spo.SearchableProjectObjects:
        """
        Return a `spo.SearchableProjectObjects` instance of all the wells for this project.

        Returns:
            An `spo.SearchableProjectObjects` for all the wells of this project.
        """
        return spo.SearchableProjectObjects(nwa.NativeWellAdapter, self.dom_object.Wells.Items)

    def wells_by_name(self, name) -> Iterable[IWell]:
        """
        Return all the wells in this project with the specified name.
        :param name: The name of the well(s) of interest.
        :return: A list of all the wells in this project.
        """
        return toolz.filter(lambda w: name == w.name, self.wells)
