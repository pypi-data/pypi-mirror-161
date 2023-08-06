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

import enum

import orchid.base
from orchid import (
    base_time_series_adapter as bca,
    dot_net_dom_access as dna,
)

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.TimeSeries import IQuantityTimeSeries


class TreatmentCurveTypes(enum.Enum):
    DOWNHOLE_PROPPANT_CONCENTRATION = 'Downhole Proppant Concentration'
    SURFACE_PROPPANT_CONCENTRATION = 'Surface Proppant Concentration'
    SLURRY_RATE = 'Slurry Rate'
    TREATING_PRESSURE = 'Pressure'


class NativeTreatmentCurveAdapter(bca.BaseTimeSeriesAdapter):
    suffix = dna.dom_property('suffix', 'Return the suffix for this treatment curve.')

    def __init__(self, net_treatment_curve: IQuantityTimeSeries):
        super().__init__(net_treatment_curve, orchid.base.constantly(net_treatment_curve.Stage.Well.Project))

    def quantity_name_unit_map(self, project_units):
        """
        Return a map (dictionary) between quantity names and units (from `unit_system`) of the data_points.

        This method plays the role of "Primitive Operation" in the *Template Method* design pattern. In this
        role, the "Template Method" defines an algorithm and delegates some steps of the algorithm to derived
        classes through invocation of "Primitive Operations".

        Args:
            project_units: The unit system of the project.
        """
        result = {
            TreatmentCurveTypes.TREATING_PRESSURE.value: project_units.PRESSURE,
            TreatmentCurveTypes.DOWNHOLE_PROPPANT_CONCENTRATION.value: project_units.PROPPANT_CONCENTRATION,
            TreatmentCurveTypes.SURFACE_PROPPANT_CONCENTRATION.value: project_units.PROPPANT_CONCENTRATION,
            TreatmentCurveTypes.SLURRY_RATE.value: project_units.SLURRY_RATE,
        }
        return result
