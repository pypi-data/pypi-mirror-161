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


import dataclasses as dc
from enum import IntEnum
import math
from typing import Optional, Tuple, Union

import deal
import option
import pendulum as pdt
import toolz.curried as toolz

import orchid.base
from orchid import (
    dot_net_disposable as dnd,
    dot_net_dom_access as dna,
    dom_project_object as dpo,
    measurement as om,
    native_stage_part_adapter as spa,
    native_subsurface_point as nsp,
    native_treatment_curve_adapter as ntc,
    net_date_time as ndt,
    net_fracture_diagnostics_factory as fdf,
    net_quantity as onq,
    reference_origins as origins,
    searchable_stage_parts as ssp,
    unit_system as units,
    validation
)

# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics import FormationConnectionType, IStagePart
# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics.Factories import Calculations
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.SDKFacade import ScriptAdapter
# noinspection PyUnresolvedReferences
import UnitsNet
# noinspection PyUnresolvedReferences
from System.Collections.Generic import List
# noinspection PyUnresolvedReferences
import System


VALID_LENGTH_UNIT_MESSAGE = 'The parameter, `in_length_unit`, must be a unit system length.'


_object_factory = fdf.create()


class ConnectionType(IntEnum):
    PLUG_AND_PERF = FormationConnectionType.PlugAndPerf,
    SLIDING_SLEEVE = FormationConnectionType.SlidingSleeve,
    SINGLE_POINT_ENTRY = FormationConnectionType.SinglePointEntry,
    OPEN_HOLE = FormationConnectionType.OpenHole


def as_connection_type(type_value):
    @toolz.curry
    def has_value(value, enum_type):
        return value == enum_type.value

    return toolz.pipe(iter(ConnectionType),
                      toolz.filter(has_value(type_value)),
                      toolz.nth(0))


# This pre-condition applies to the public methods:
# - bottom_location
# - center_location
# - cluster_location
# - top_location
# but is implemented here to ensure common behavior among all these public methods.
@deal.pre(lambda _depth_datum, _reference_frame, in_length_unit, _net_subsurface_point_func:
          validation.is_unit_system_length(in_length_unit),
          message=VALID_LENGTH_UNIT_MESSAGE)
def subsurface_point_in_length_unit(depth_datum: origins.DepthDatum,
                                    xy_reference_frame: origins.WellReferenceFrameXy,
                                    in_length_unit: Union[units.UsOilfield, units.Metric],
                                    net_subsurface_point_func) -> nsp.SubsurfacePoint:
    """
    Calculate the subsurface point `in_length_unit` whose value is calculated by the
    callable, `net_subsurface_point_func`.

    Although this method is public, the author intends it to be "private." The author has made it public
    **only** to support unit testing. No other usage is supported.

    Args:
        depth_datum: The datum from which we measure depths.
        xy_reference_frame: The reference frame for easting-northing coordinates.
        in_length_unit: The unit of length available from the returned value.
        net_subsurface_point_func: The callable to calculate the subsurface point in .NET.

    Returns:
        The subsurface point in the requested unit of length.
    """
    net_subsurface_point = net_subsurface_point_func(xy_reference_frame.value, depth_datum.value)
    result = nsp.SubsurfacePoint(net_subsurface_point, in_length_unit)
    return result


class NativeStageAdapter(dpo.DomProjectObject):
    """Adapts a .NET IStage to be more Pythonic."""

    def __init__(self, adaptee, calculations_factory=None):
        super().__init__(adaptee, orchid.base.constantly(adaptee.Well.Project))
        self.calculations_factory = Calculations.FractureDiagnosticsCalculationsFactory() \
            if not calculations_factory else calculations_factory

    cluster_count = dna.dom_property('number_of_clusters', 'The number of clusters for this stage')
    display_name_with_well = dna.dom_property('display_name_with_well',
                                              'The display stage number including the well name')
    display_name_without_well = dna.dom_property('display_name_without_well',
                                                 'The display stage number excluding the well name')
    display_stage_number = dna.dom_property('display_stage_number', 'The display stage number for the stage')
    global_stage_sequence_number = dna.dom_property('global_stage_sequence_number',
                                                    'The global sequence number of this stage')
    order_of_completion_on_well = dna.dom_property('order_of_completion_on_well',
                                                   'The order in which this stage was completed on its well')
    stage_type = dna.transformed_dom_property('stage_type', 'The formation connection type of this stage',
                                              as_connection_type)
    start_time = dna.transformed_dom_property('start_time', 'The start time of the stage treatment',
                                              ndt.as_date_time)
    stop_time = dna.transformed_dom_property('stop_time', 'The stop time of the stage treatment',
                                             ndt.as_date_time)

    def _get_time_range(self) -> pdt.Period:
        return pdt.period(self.start_time, self.stop_time)

    def _set_time_range(self, to_time_range: pdt.Period):
        to_start_net_time = ndt.as_net_date_time(to_time_range.start)
        to_stop_net_time = ndt.as_net_date_time(to_time_range.end)
        if len(self.stage_parts()) == 1:
            single_stage_part = toolz.first(self.stage_parts())
            with dnd.disposable(single_stage_part.dom_object.ToMutable()) as mutable_first_stage_part:
                mutable_first_stage_part.SetStartStopTimes(to_start_net_time,
                                                           to_stop_net_time)
        elif len(self.stage_parts()) > 1:
            single_stage_part = toolz.first(self.stage_parts())
            with dnd.disposable(single_stage_part.dom_object.ToMutable()) as mutable_first_stage_part:
                mutable_first_stage_part.SetStartStopTimes(to_start_net_time,
                                                           single_stage_part.dom_object.StopTime)
            last_stage_part = toolz.last(self.stage_parts())
            with dnd.disposable(last_stage_part.dom_object.ToMutable()) as mutable_last_stage_part:
                mutable_last_stage_part.SetStartStopTimes(last_stage_part.dom_object.StartTime,
                                                          to_stop_net_time)
        else:  # No stage parts
            factory = fdf.create()
            stage_part_to_add = factory.CreateStagePart(self.dom_object, to_start_net_time,
                                                        to_stop_net_time, None)
            with dnd.disposable(self.dom_object.ToMutable()) as mutable_stage:
                mutable_stage.Parts.Add(stage_part_to_add)

    time_range = property(fget=_get_time_range, fset=_set_time_range,
                          doc='The time range (start and end) of this stage')

    @property
    def isip(self) -> om.Quantity:
        """
        Return the instantaneous shut in pressure of this stage in project units.
        """
        return onq.as_measurement_from_option(self.expect_project_units.PRESSURE, self.dom_object.Isip)

    @property
    def pnet(self) -> om.Quantity:
        """
        Return the net pressure of this stage in project units.

        The net pressure of a stage is calculated by the formula:
            pnet = isip + fluid-density * tvd - shmin (where tvd is the true vertical depth)
        """
        return onq.as_measurement_from_option(self.expect_project_units.PRESSURE, self.dom_object.Pnet)

    @property
    def shmin(self) -> om.Quantity:
        """
        Return the minimum horizontal stress of this stage in project units.
        """

        return onq.as_measurement_from_option(self.expect_project_units.PRESSURE, self.dom_object.Shmin)

    @staticmethod
    def _sampled_quantity_name_curve_map(sampled_quantity_name):
        candidates = toolz.pipe(ntc.TreatmentCurveTypes,
                                toolz.filter(lambda e: e.value == sampled_quantity_name),
                                list)
        if len(candidates) == 0:
            raise KeyError(f'Unknown sampled quantity name: "{sampled_quantity_name}"')

        assert len(candidates) == 1, f'Sampled quantity name "{sampled_quantity_name}"' \
                                     f' selects many curve types: {candidates}'

        return candidates[0]

    def _center_location_depth(self, in_length_unit: Union[units.UsOilfield, units.Metric],
                               depth_datum: origins.DepthDatum) -> om.Quantity:
        """
        Return the depth of the stage center relative to the specified `depth_datum.`

        Args:
            in_length_unit: The unit of length for the returned Measurement.
            depth_datum: The reference datum for the depth.
        """
        subsurface_point = self.center_location(in_length_unit, origins.WellReferenceFrameXy.ABSOLUTE_STATE_PLANE,
                                                depth_datum)
        return subsurface_point.depth

    def bottom_location(self, in_length_unit: Union[units.UsOilfield, units.Metric],
                        xy_reference_frame: origins.WellReferenceFrameXy,
                        depth_datum: origins.DepthDatum) -> nsp.SubsurfacePoint:
        """
        Return the location of the bottom of this stage in the `xy_well_reference_frame` using the
        `depth_datum` in the specified unit.

        Args:
            in_length_unit: The unit of length available from the returned value.
            xy_reference_frame: The reference frame for easting-northing coordinates.
            depth_datum: The datum from which we measure depths.

        Returns:
            The `SubsurfacePoint` of the stage bottom.
        """

        return subsurface_point_in_length_unit(depth_datum, xy_reference_frame, in_length_unit,
                                               self.dom_object.GetStageLocationBottom)

    def center_location(self, in_length_unit: Union[units.UsOilfield, units.Metric],
                        xy_reference_frame: origins.WellReferenceFrameXy,
                        depth_datum: origins.DepthDatum) -> nsp.SubsurfacePoint:
        """
        Return the location of the center of this stage in the `xy_well_reference_frame` using the `depth_datum`
        in the specified unit.

        Args:
            in_length_unit: The unit of length available from the returned value.
            xy_reference_frame: The reference frame for easting-northing coordinates.
            depth_datum: The datum from which we measure depths.

        Returns:
            The `SubsurfacePoint` of the stage center.
        """
        return subsurface_point_in_length_unit(depth_datum, xy_reference_frame, in_length_unit,
                                               self.dom_object.GetStageLocationCenter)

    def center_location_easting(self, in_length_unit: Union[units.UsOilfield, units.Metric],
                                xy_well_reference_frame: origins.WellReferenceFrameXy) -> om.Quantity:
        """
        Return the easting location of the stage center relative to the specified reference frame in the
        specified unit.

        Args:
            in_length_unit: An unit of the unit of length for the returned Measurement.
            xy_well_reference_frame: The reference frame defining the origin.

        Returns:
            A measurement.
        """
        result = self.center_location(in_length_unit, xy_well_reference_frame, origins.DepthDatum.KELLY_BUSHING).x
        return result

    def center_location_northing(self, in_length_unit: Union[units.UsOilfield, units.Metric],
                                 xy_well_reference_frame: origins.WellReferenceFrameXy) -> om.Quantity:
        """
        Return the northing location of the stage center in the `xy_well_reference_frame` in the specified unit.

        Args:
            in_length_unit: The requested resultant length unit.
            xy_well_reference_frame: The reference frame defining the origin.

        Returns:
            A measurement.
        """
        subsurface_point = self.center_location(in_length_unit, xy_well_reference_frame,
                                                origins.DepthDatum.KELLY_BUSHING)
        return subsurface_point.y

    def center_location_mdkb(self, in_length_unit: Union[units.UsOilfield, units.Metric]) -> om.Quantity:
        """
        Return the measured depth of the stage center in project units.

        Args:
            in_length_unit: The unit of length for the returned Measurement.
        """
        return (self.md_top(in_length_unit) + self.md_bottom(in_length_unit)) / 2

    def center_location_tvdgl(self, in_length_unit: Union[units.UsOilfield, units.Metric]) -> om.Quantity:
        """
        Returns the total vertical depth from ground level of the stage center in project units.

        Args:
            in_length_unit: The unit of length for the returned Measurement.
        """
        return self._center_location_depth(in_length_unit, origins.DepthDatum.GROUND_LEVEL)

    def center_location_tvdss(self, in_length_unit: Union[units.UsOilfield, units.Metric]) -> om.Quantity:
        """
        Returns the total vertical depth from sea level of the stage center in project units.

        Args:
            in_length_unit: The unit of length for the returned Measurement.
        """
        return self._center_location_depth(in_length_unit, origins.DepthDatum.SEA_LEVEL)

    def center_location_xy(self, in_length_unit: Union[units.UsOilfield, units.Metric],
                           xy_well_reference_frame: origins.WellReferenceFrameXy) -> Tuple[om.Quantity,
                                                                                           om.Quantity]:
        """
        Return the easting-northing location of the stage center in the `xy_well_reference_frame` in project units.

        Args:
            in_length_unit: The unit of length for the returned Measurement.
            xy_well_reference_frame: The reference frame defining the origin.

        Returns:
            A tuple
        """
        subsurface_point = self.center_location(in_length_unit, xy_well_reference_frame,
                                                origins.DepthDatum.KELLY_BUSHING)
        return subsurface_point.x, subsurface_point.y

    @deal.pre(lambda _self, _in_length_unit, cluster_no, _xy_reference_frame, _depth_datum: cluster_no >= 0)
    def cluster_location(self, in_length_unit: Union[units.UsOilfield, units.Metric], cluster_no: int,
                         xy_reference_frame: origins.WellReferenceFrameXy,
                         depth_datum: origins.DepthDatum) -> nsp.SubsurfacePoint:
        """
        Return the location of the bottom of this stage in the `xy_well_reference_frame` using the
        `depth_datum` in the specified unit.

        Args:
            in_length_unit: The unit of length available from the returned value.
            cluster_no: The number identifying the cluster whose location is sought.
            xy_reference_frame: The reference frame for easting-northing coordinates.
            depth_datum: The datum from which we measure depths.

        Returns:
            The `SubsurfacePoint` of the stage cluster identified by `cluster_no`.
        """
        stage_location_cluster_func = toolz.curry(self.dom_object.GetStageLocationCluster, cluster_no)
        return subsurface_point_in_length_unit(depth_datum, xy_reference_frame, in_length_unit,
                                               stage_location_cluster_func)

    @deal.pre(validation.arg_is_acceptable_pressure_unit)
    def isip_in_pressure_unit(self, target_unit: Union[units.UsOilfield, units.Metric]) -> om.Quantity:
        return onq.as_measurement_from_option(target_unit, self.dom_object.Isip)

    def md_bottom(self, in_length_unit: Union[units.UsOilfield, units.Metric]):
        """
        Return the measured depth of the bottom of this stage (farthest from the wellhead / closest to the toe)
        in the specified unit.

        Args:
            in_length_unit: An unit of the unit of length for the returned Measurement.

        Returns:
             The measured depth of the stage bottom in the specified unit.
        """
        return onq.as_measurement(in_length_unit, option.maybe(self.dom_object.MdBottom))

    def md_top(self, in_length_unit: Union[units.UsOilfield, units.Metric]) -> om.Quantity:
        """
        Return the measured depth of the top of this stage (closest to the wellhead / farthest from the toe)
        in the specified unit.

        Args:
            in_length_unit: An unit of the requested resultant length unit.

        Returns;
         The measured depth of the stage top in the specified unit.
        """
        return onq.as_measurement(in_length_unit, option.maybe(self.dom_object.MdTop))

    @deal.pre(validation.arg_is_acceptable_pressure_unit)
    def pnet_in_pressure_unit(self, target_unit: Union[units.UsOilfield, units.Metric]) -> om.Quantity:
        return onq.as_measurement_from_option(target_unit, self.dom_object.Pnet)

    @deal.pre(validation.arg_is_acceptable_pressure_unit)
    def shmin_in_pressure_unit(self, target_unit: Union[units.UsOilfield, units.Metric]) -> om.Quantity:
        return onq.as_measurement_from_option(target_unit, self.dom_object.Shmin)

    def stage_length(self, in_length_unit: Union[units.UsOilfield, units.Metric]) -> om.Quantity:
        """
        Return the stage length in the specified unit.

        Args:
            in_length_unit: An unit of the unit of length for the returned Measurement.

        Returns:
            The Measurement of the length of this stage.
        """
        return self.md_bottom(in_length_unit) - self.md_top(in_length_unit)

    def stage_parts(self) -> ssp.SearchableStageParts:
        """
        Return a `ssp.SearchableStageParts` for all the stage parts for this stage.

        Returns:
            An `ssp.SearchableStageParts` for all the stage parts for this stage.
        """
        return ssp.SearchableStageParts(spa.NativeStagePartAdapter, self.dom_object.Parts)

    def top_location(self, in_length_unit: Union[units.UsOilfield, units.Metric],
                     xy_reference_frame: origins.WellReferenceFrameXy,
                     depth_datum: origins.DepthDatum) -> nsp.SubsurfacePoint:
        """
        Return the location of the top of this stage in the `xy_well_reference_frame` using the `depth_datum`
        in the specified unit.

        Args:
            in_length_unit: The unit of length available from the returned value.
            xy_reference_frame: The reference frame for easting-northing coordinates.
            depth_datum: The datum from which we measure depths.

        Returns:
            The `SubsurfacePoint` of the stage top.
        """
        return subsurface_point_in_length_unit(depth_datum, xy_reference_frame, in_length_unit,
                                               self.dom_object.GetStageLocationTop)

    def treatment_curves(self):
        """
        Returns the dictionary of treatment curves for this treatment_stage.

        Request a specific curve from the dictionary using the constants defined in `orchid`:

        - `PROPPANT_CONCENTRATION`
        - `SLURRY_RATE`
        - `TREATING_PRESSURE`

        Returns:
            The dictionary containing the available treatment curves.
        """
        if not self.dom_object.TreatmentCurves.Items:
            return {}

        def add_curve(so_far, treatment_curve):
            curve_name = self._sampled_quantity_name_curve_map(treatment_curve.sampled_quantity_name)
            treatment_curve_map = {curve_name: treatment_curve}
            return toolz.merge(treatment_curve_map, so_far)

        result = toolz.pipe(self.dom_object.TreatmentCurves.Items,  # start with .NET treatment curves
                            toolz.map(ntc.NativeTreatmentCurveAdapter),  # wrap them in a facade
                            # Transform the map to a dictionary keyed by the sampled quantity name
                            lambda cs: toolz.reduce(add_curve, cs, {}))
        return result


@dc.dataclass
class CreateStageDto:
    """
    A data-transfer object (DTO) containing the required and optional data used to create new stages.

    This class enforces a number of constraints on the data needed to create a stage. Consider viewing the source
    code of the class to understand those constraints. (The class will throw exceptions if the constraints are not met
    at run-time.)

    Additionally, the comments of this class contain a number of "warnings" for situations where data is not required,
    but the consequences for **not** supplying the data may not be desirable or may not be expected.
    """
    stage_no: int  # Must be positive
    connection_type: ConnectionType
    md_top: om.Quantity  # Must be length
    md_bottom: om.Quantity  # Must be length

    cluster_count: int = 0  # Must be non-negative
    maybe_shmin: Optional[om.Quantity] = None  # If not `None`, must be pressure
    # WARNING: one need supply neither a start time nor a stop time; however, not supplying this data can
    # produce unexpected behavior for the `global_stage_sequence_number` property. For example, one can
    # generate duplicate values for the `global_stage_sequence_number`. This unexpected behavior is a known
    # issue with Orchid.
    #
    # Note supplying no value (an implicit `None`) results in the largest possible .NET time range.
    maybe_time_range: Optional[pdt.Period] = None
    # WARNING: one must currently supply an ISIP for each stage; otherwise, Orchid fails to correctly load
    # the project saved with the added stages.
    maybe_isip: Optional[om.Quantity] = None  # If not `None`, must be a pressure

    order_of_completion_on_well = property(fget=lambda self: self.stage_no - 1)

    def __post_init__(self):
        # See the
        # [StackOverflow post](https://stackoverflow.com/questions/54488765/validating-input-when-mutating-a-dataclass)
        if self.stage_no <= 0:
            raise ValueError(f'Expected stage_no to be positive. Found {self.stage_no}')
        if not self.md_top.check('[length]'):
            raise ValueError(f'Expected md_top to be a length. Found {self.md_top:~P}')
        if not self.md_bottom.check('[length]'):
            raise ValueError(f'Expected md_bottom to be a length. Found {self.md_bottom:~P}')
        if self.cluster_count < 0:
            raise ValueError(f'Expected cluster_count to be non-negative. Found {self.cluster_count}')
        if self.maybe_isip is not None:
            if not self.maybe_isip.check('[pressure]'):
                raise ValueError(f'Expected maybe_isip to be a pressure if not None. Found {self.maybe_isip:~P}')
        if self.maybe_shmin is not None:
            if not self.maybe_shmin.check('[pressure]'):
                raise ValueError(f'Expected maybe_shmin to be a pressure if not None. Found {self.maybe_shmin:~P}')

    def create_stage(self, well) -> NativeStageAdapter:
        """
        Creates a stage from this DTO.

        Args:
            well (NativeWellAdapter): The well of the created `NativeStageAdapter`

        Returns:
            The `NativeStageAdapter` wrapping the created .NET `IStage` instance.

        """
        project_unit_system = units.as_unit_system(well.dom_object.Project.ProjectUnits)
        native_md_top = onq.as_net_quantity(project_unit_system.LENGTH, self.md_top)
        native_md_bottom = onq.as_net_quantity(project_unit_system.LENGTH, self.md_bottom)
        if self.maybe_shmin is None:
            native_shmin = ScriptAdapter.MakeOptionNone[UnitsNet.Pressure]()
        elif math.isnan(self.maybe_shmin.magnitude):
            native_shmin = ScriptAdapter.MakeOptionNone[UnitsNet.Pressure]()
        else:
            native_shmin = ScriptAdapter.MakeOptionSome(
                onq.as_net_quantity(project_unit_system.PRESSURE, self.maybe_shmin))
        completion_order_on_well = System.UInt32(self.order_of_completion_on_well)
        connection_type = self.connection_type.value
        cluster_count = System.UInt32(self.cluster_count)
        no_time_range_native_stage = self.create_net_stage(well.dom_object, completion_order_on_well,
                                                           connection_type, native_md_top,
                                                           native_md_bottom, native_shmin,
                                                           cluster_count)

        with dnd.disposable(no_time_range_native_stage.ToMutable()) as mutable_stage:
            native_start_time = (ndt.as_net_date_time(self.maybe_time_range.start)
                                 if self.maybe_time_range is not None
                                 else pdt.DateTime.max)
            native_stop_time = (ndt.as_net_date_time(self.maybe_time_range.end)
                                if self.maybe_time_range is not None
                                else pdt.DateTime.max)
            if self.maybe_isip is None:
                native_isip = None
            elif math.isnan(self.maybe_isip.magnitude):
                native_isip = None
            else:
                native_isip = onq.as_net_quantity(project_unit_system.PRESSURE, self.maybe_isip)

            stage_part = self.create_net_stage_part(no_time_range_native_stage, native_start_time, native_stop_time,
                                                    native_isip)
            self.add_stage_part_to_stage(mutable_stage, stage_part)

        # Alias to better communicate intent
        created_native_stage = no_time_range_native_stage
        return NativeStageAdapter(created_native_stage)

    @staticmethod
    def create_net_stage(native_well, completion_order_on_well, connection_type, native_md_top, native_md_bottom,
                         native_shmin, cluster_count):
        """
        Create a .NET `IStage`.

        This method primarily exists so that I can mock the call in unit tests.

        Args:
            native_well: The .NET `IWell` instance to which the created `IStage` refers.
            completion_order_on_well: The order of completion of this stage of the referenced `IWell`.
            connection_type: The .NET `FormationConnectionType` of the created .NET stage.
            native_md_top: The measured depth of the top (toward the heel) of the created .NET stage.
            native_md_bottom: The measured depth of the bottom (toward the toe) of the created .NET stage.
            native_shmin: The minimum horizontal stress of the created .NET stage.
            cluster_count: The cluster count of the created .NET stage.

        Returns:
            The newly created .NET `IStage` instance.
        """
        no_time_range_native_stage = _object_factory.CreateStage(
            System.UInt32(completion_order_on_well),
            native_well,
            connection_type,
            native_md_top,
            native_md_bottom,
            native_shmin,
            System.UInt32(cluster_count)
        )
        return no_time_range_native_stage

    @staticmethod
    def create_net_stage_part(native_stage, native_start_time, native_stop_time, native_isip):
        """
        Create . .NET `IStagePart` instance.

        This method primarily exists so that I can mock the call in unit tests.

        Args:
            native_stage: The .NET `IStage` to which the created `IStagePart` refers.
            native_start_time: The start time of the created `IStagePart`.
            native_stop_time: The stop time of the created `IStagePart`.
            native_isip: The ISIP of the created `IStagePart`.

        Returns:
            The newly created `IStagePart` with the specified details.
        """
        stage_part = _object_factory.CreateStagePart(native_stage,
                                                     native_start_time,
                                                     native_stop_time,
                                                     native_isip)
        return stage_part

    @staticmethod
    def add_stage_part_to_stage(mutable_stage, stage_part):
        """
        Add a newly created `stage_part` to a newly created `mutable_stage`.

        This method exists primarily so that I can mock it for unit tests.

        Args:
            mutable_stage: The newly created stage supporting mutability.
            stage_part: The newly created stage part.
        """
        stage_parts = List[IStagePart]()
        stage_parts.Add(stage_part)
        mutable_stage.Parts = stage_parts
