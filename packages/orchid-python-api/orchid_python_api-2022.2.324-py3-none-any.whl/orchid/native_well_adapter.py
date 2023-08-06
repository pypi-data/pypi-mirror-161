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
from typing import Iterable

import option
import toolz.curried as toolz

import orchid.base
from orchid import (
    dot_net_dom_access as dna,
    dot_net_disposable as dnd,
    dom_project_object as dpo,
    searchable_stages as oss,
    measurement as om,
    native_stage_adapter as nsa,
    native_subsurface_point as nsp,
    native_trajectory_adapter as nta,
    net_quantity as onq,
    reference_origins as origins,
)

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import IStage, IWell
# noinspection PyUnresolvedReferences
import UnitsNet
# noinspection PyUnresolvedReferences
from System import Array, UInt32

WellHeadLocation = namedtuple('WellHeadLocation',
                              ['easting', 'northing', 'depth'])


def replace_no_uwi_with_text(uwi):
    return uwi if uwi else 'No UWI'


class NativeWellAdapter(dpo.DomProjectObject):
    """Adapts a native IWell to python."""

    def __init__(self, net_well: IWell):
        """
        Constructs an instance adapting a .NET IWell.

        Args:
            net_well: The .NET well to be adapted.
        """
        super().__init__(net_well, orchid.base.constantly(net_well.Project))

    trajectory = dna.transformed_dom_property('trajectory', 'The trajectory of the adapted .NET well.',
                                              nta.NativeTrajectoryAdapterIdentified)
    uwi = dna.transformed_dom_property('uwi', 'The UWI of the adapted .', replace_no_uwi_with_text)

    # The formation property **does not** check when a `None` value is passed from Orchid.
    # Although it is possible, it is very unlikely to occur from IWell.Formation.
    formation = dna.dom_property('formation', 'The production formation the well is landed')

    @property
    def ground_level_elevation_above_sea_level(self) -> om.Quantity:
        return onq.as_measurement(self.expect_project_units.LENGTH,
                                  option.maybe(self.dom_object.GroundLevelElevationAboveSeaLevel))

    @property
    def kelly_bushing_height_above_ground_level(self) -> om.Quantity:
        return onq.as_measurement(self.expect_project_units.LENGTH,
                                  option.maybe(self.dom_object.KellyBushingHeightAboveGroundLevel))

    @property
    def wellhead_location(self):
        dom_whl = self.dom_object.WellHeadLocation
        result = toolz.pipe(dom_whl,
                            toolz.map(option.maybe),
                            toolz.map(onq.as_measurement(self.expect_project_units.LENGTH)),
                            list, )
        return WellHeadLocation(*result)

    def stages(self) -> oss.SearchableStages:
        """
        Return a `spo.SearchableProjectObjects` instance of all the stages for this project.

        Returns:
            An `spo.SearchableProjectObjects` for all the stages of this project.
        """
        return oss.SearchableStages(nsa.NativeStageAdapter, self.dom_object.Stages.Items)

    def locations_for_md_kb_values(self,
                                   md_kb_values: Iterable[om.Quantity],
                                   well_reference_frame_xy: origins.WellReferenceFrameXy,
                                   depth_origin: origins.DepthDatum) -> Iterable[nsp.SubsurfacePoint]:
        sample_at = Array[UnitsNet.Length](toolz.map(onq.as_net_quantity(self.expect_project_units.LENGTH),
                                                     md_kb_values))
        result = toolz.pipe(
            self.dom_object.GetLocationsForMdKbValues(sample_at, well_reference_frame_xy, depth_origin),
            toolz.map(nsp.make_subsurface_point(self.expect_project_units.LENGTH)),
            list,
        )
        return result

    def add_stages(self, create_stage_dtos: Iterable[nsa.CreateStageDto]):
        created_stages = [csd.create_stage(self) for csd in create_stage_dtos]

        with dnd.disposable(self.dom_object.ToMutable()) as mutable_well:
            native_created_stages = self._create_net_stages(created_stages)
            mutable_well.AddStages(native_created_stages)

    @staticmethod
    def _create_net_stages(created_stages):
        """
        Create a .NET `Array<IStage>`.

        This method primarily exists so that I can mock the call in unit tests.

        Args:
            created_stages: The `NativeStageAdapter` iterable over the created stages to add.

        Returns:
            The newly created .NET `Array<IStage>` instance.
        """
        return Array[IStage]([created_stage.dom_object for created_stage in created_stages])
