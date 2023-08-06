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

"""This module contains functions for converting between instances of the (Python) `Measurement` class and
instances of .NET classes like `UnitsNet.Quantity` and `DateTime`."""

from functools import singledispatch
import math
from numbers import Real
import operator
from typing import Optional, Union

import option
import toolz.curried as toolz

from orchid import (
    measurement as om,
    physical_quantity as opq,
    unit_system as units,
)

# noinspection PyUnresolvedReferences
from Optional import Option
# noinspection PyUnresolvedReferences
import System
# noinspection PyUnresolvedReferences
import UnitsNet


# Convenience functions


def to_net_quantity_value(magnitude):
    """
    Create a `UnitsNet` `QuantityValue` instance.

    The `UnitsNet` package *does not* accept floating point values to create most measurements; instead, these
    creation functions expect an argument of type `QuantityValue`. In .NET, these values are created using an
    implicit conversion. This implicit version on the Python side fails.

    This function allows us to define that conversion in one place.

    Args:
        magnitude: The magnitude of the `UnitNet` `Quantity` (measurement) to be created.

    Returns:
        The `magnitude` wrapped in a `UnitsNet.QuantityValue` instance.

    """
    return UnitsNet.QuantityValue.op_Implicit(magnitude)


def net_length_from(magnitude: float, net_unit: UnitsNet.Length.Units) -> UnitsNet.Quantity:
    """
    Create a `UnitsNet` length measurement from `magnitude` and `net_unit`.

    Args:
        magnitude: The magnitude of the length measurement
        net_unit: The `UnitsNet` unit of the length measurement

    Returns:
        The `UnitsNet` `Quantity` whose `Value` is `magnitude` and whose `Unit` is `net_unit`.
    """
    return UnitsNet.Length.From(to_net_quantity_value(magnitude), net_unit)


def net_pressure_from(magnitude: float, net_unit: UnitsNet.Pressure.Units) -> UnitsNet.Quantity:
    """
    Create a `UnitsNet` pressure measurement from `magnitude` and `net_unit`.

    Args:
        magnitude: The magnitude of the pressure measurement
        net_unit: The `UnitsNet` unit of the pressure measurement

    Returns:
        The `UnitsNet` `Quantity` whose `Value` is `magnitude` and whose `Unit` is `net_unit`.
    """
    return UnitsNet.Pressure.From(to_net_quantity_value(magnitude), net_unit)


# The following code creates conversion functions programmatically by:
# - Creating a map from variable name to string identifying how to create the `UnitsNet` `Quantity`
# - Transforming that map by:
#   - Transforming the map keys by prepending 'net_'
#   - Transforming the map values to a function creating the value. (See the documentation of
#     `operator.attrgetter` function for details.)
# - Adding the key and value of this map to the `globals()` dict (module attributes)
net_creator_attributes = {
    'angle_from_deg': 'Angle.FromDegrees',
    'duration_from_min': 'Duration.FromMinutes',
    'density_from_lbs_per_cu_ft': 'Density.FromPoundsPerCubicFoot',
    'density_from_kg_per_cu_m': 'Density.FromKilogramsPerCubicMeter',
    'energy_from_ft_lbs': 'Energy.FromFootPounds',
    'energy_from_J': 'Energy.FromJoules',
    'force_from_lbf': 'Force.FromPoundsForce',
    'force_from_N': 'Force.FromNewtons',
    'length_from_ft': 'Length.FromFeet',
    'length_from_m': 'Length.FromMeters',
    'mass_from_lbs': 'Mass.FromPounds',
    'mass_from_kg': 'Mass.FromKilograms',
    'power_from_hp': 'Power.FromMechanicalHorsepower',
    'power_from_W': 'Power.FromWatts',
    'pressure_from_psi': 'Pressure.FromPoundsForcePerSquareInch',
    'pressure_from_kPa': 'Pressure.FromKilopascals',
    'pressure_from_bars': 'Pressure.FromBars',
    'mass_concentration_from_lbs_per_gal': 'MassConcentration.FromPoundsPerUSGallon',
    'mass_concentration_from_kg_per_cu_m': 'MassConcentration.FromKilogramsPerCubicMeter',
    'volume_flow_from_oil_bbl_per_min': 'VolumeFlow.FromOilBarrelsPerMinute',
    'volume_flow_from_cu_m_per_min': 'VolumeFlow.FromCubicMetersPerMinute',
    'temperature_from_deg_F': 'Temperature.FromDegreesFahrenheit',
    'temperature_from_deg_C': 'Temperature.FromDegreesCelsius',
    'volume_from_oil_bbl': 'Volume.FromOilBarrels',
    'volume_from_cu_m': 'Volume.FromCubicMeters',
}
net_creator_funcs = toolz.pipe(
    net_creator_attributes,
    toolz.keymap(lambda k: f'net_{k}'),
    toolz.valmap(lambda v: toolz.compose(operator.attrgetter(v)(UnitsNet),
                                         to_net_quantity_value)),
)
for variable_name, variable_value in net_creator_funcs.items():
    globals()[variable_name] = variable_value


class EqualsComparisonDetails:
    def __init__(self, tolerance: Real = 1e-4,
                 net_comparison_type: UnitsNet.ComparisonType = UnitsNet.ComparisonType.Relative):
        """
        Construct an instance that uses `tolerance` and `comparison_type` to determine equality.

        This class exists because the `tolerance` and `comparison_type` are closely coupled; that is, one
        cannot correctly interpret the use of `tolerance` without a reference to the `comparison_type`.

        Args:
            tolerance: The maximum difference tolerated between two instances in determining equality.
            net_comparison_type: The type of comparison: `UnitsNet.ComparisonType.Relative` or
            `UnitsNet.ComparisonType.Absolute`.
        """
        self._tolerance = tolerance
        self._comparison_type = net_comparison_type

    @property
    def tolerance(self) -> Real:
        """
        Return the tolerance to be use in determining equality.

        Although this property is public, it is intended only to be read by the `equal_net_comparison`
        function.
        """
        return self._tolerance

    @property
    def comparison_type(self) -> UnitsNet.ComparisonType:
        """
        Return the comparison type to be use in determining equality.

        Although this property is public, it is intended only to be read by the `equal_net_comparison`
        function.
        """
        return self._comparison_type


#
# Although Pint supports the unit `cu_ft`, we have chosen to use the synonym, `ft ** 3` (which is
# printed as 'ft\u00b3` (that is, 'ft' followed by a Unicode superscript 3)). According to a
# citation on [Wikipedia article](https://en.wikipedia.org/wiki/Cubic_foot), this "is the IEEE
# symbol for the cubic foot." Our general rule: we accept the Pint unit `cu_ft` as **input**,
# but, on various conversion, produce the Pint unit `ft**3`.
#


@singledispatch
@toolz.curry
def as_measurement(unknown, _maybe_net_quantity: option.Option[UnitsNet.IQuantity]) -> om.Quantity:
    """
    Convert an optional .NET `IQuantity` to a `pint` `Quantity` instance.

    This function is registered as the type-handler for the `object` type. In our situation, arriving here
    indicates an error by an implementer and so raises an error.

    Args:
        unknown: A parameter whose type is not expected.
        _maybe_net_quantity: The optional .NET `IQuantity` instance to convert. (Unused.)
    """
    raise TypeError(f'First argument, {unknown}, has type {type(unknown)}, unexpected by `as_measurement`.')


# noinspection PyUnresolvedReferences
@as_measurement.register(units.Common)
@toolz.curry
def as_measurement_in_common_unit(target_unit, maybe_net_quantity: UnitsNet.IQuantity) -> om.Quantity:
    """
    Convert an optional .NET `IQuantity` to a `pint` `Quantity` instance in a common unit.

    Args:
        target_unit: The unit (from the units.Common) for the converted `Quantity` instance.
        maybe_net_quantity: The optional .NET `IQuantity` instance to convert.

    Returns:
        The equivalent `Quantity` instance in the target unit.
    """
    return maybe_net_quantity.map_or(_as_measurement_in_unit(target_unit),
                                     om.Quantity(float('NaN'), target_unit.value.unit))


@as_measurement.register(units.Metric)
@as_measurement.register(units.UsOilfield)
@toolz.curry
def as_measurement_in_specified_unit(target_unit,
                                     maybe_net_quantity: option.Option[UnitsNet.IQuantity]) -> om.Quantity:
    """
    Convert an optional .NET `IQuantity` to a `pint` `Quantity` instance.

    Args:
        target_unit: The unit for the converted `Quantity` instance.
        maybe_net_quantity: The optional .NET `IQuantity` instance to convert.

    Returns:
        The equivalent `Quantity` instance in the target unit.
    """

    result = maybe_net_quantity.map_or(_as_measurement_in_unit(target_unit),
                                       om.Quantity(float('NaN'), target_unit.value.unit))
    return result


@toolz.curry
def _as_measurement_in_unit(target_unit: Union[units.Metric, units.UsOilfield],
                            net_quantity: UnitsNet.IQuantity) -> om.Quantity:
    """
    Convert an `IQuantity` to a `pint` `Quantity` in a specified compatible unit.

    Args:
        target_unit: The target unit for the converted `Quantity` instance.
        net_quantity: The .NET `IQuantity` instance to convert.

    Returns:
        The equivalent `Quantity` instance in the specified unit.
    """
    target_magnitude = net_quantity.As(_UNIT_NET_UNITS[target_unit])
    result = om.Quantity(target_magnitude, target_unit.value.unit)
    return result


# noinspection PyUnresolvedReferences
_physical_quantity_to_net_physical_quantity = {
    opq.PhysicalQuantity.ANGLE: UnitsNet.Angle,
    opq.PhysicalQuantity.DURATION: UnitsNet.Duration,
    opq.PhysicalQuantity.DENSITY: UnitsNet.Density,
    opq.PhysicalQuantity.ENERGY: UnitsNet.Energy,
    opq.PhysicalQuantity.FORCE: UnitsNet.Force,
    opq.PhysicalQuantity.LENGTH: UnitsNet.Length,
    opq.PhysicalQuantity.MASS: UnitsNet.Mass,
    opq.PhysicalQuantity.POWER: UnitsNet.Power,
    opq.PhysicalQuantity.PRESSURE: UnitsNet.Pressure,
    opq.PhysicalQuantity.PROPPANT_CONCENTRATION: UnitsNet.MassConcentration,
    opq.PhysicalQuantity.TEMPERATURE: UnitsNet.Temperature,
    opq.PhysicalQuantity.SLURRY_RATE: UnitsNet.VolumeFlow,
    opq.PhysicalQuantity.VOLUME: UnitsNet.Volume,
}


@toolz.curry
def _python_measurement_option(target_unit: Union[units.Metric, units.UsOilfield],
                               optional_net_quantity: Option[UnitsNet.IQuantity]):
    @toolz.curry
    def net_option_as_pythonic(net_option):
        # If we are **not** an instance of `Option<Pressure>`
        if not hasattr(net_option, 'HasValue'):
            # Simply return the value (which may be `null` / `None`)
            return net_option

        # If we **are** an instance of `Option<Pressure>` yet have no value
        if not net_option.HasValue:
            return None

        # The variable, `net_quantity`, will contain a zero value in the `UnitsNet` unit corresponding to the Python
        # physical quantity of the `target_unit`. However, because of the preceding `if` statement, I expect this
        # value to **not** be returned. (It is actually an error if it is returned; unfortunately, it is an
        # undetectable error because I cannot distinguish the zero value from a zero value actually wrapped in
        # the `Option<T>.Some` expression.
        net_physical_quantity = _physical_quantity_to_net_physical_quantity[target_unit.value.physical_quantity]
        result = net_option.ValueOr.Overloads[net_physical_quantity](net_physical_quantity.Zero)
        return result

    return toolz.pipe(
        optional_net_quantity,
        net_option_as_pythonic,
        option.maybe,
    )


def as_measurement_from_option(target_unit: Union[units.Common, units.Metric, units.UsOilfield],
                               optional_net_quantity: Option[UnitsNet.IQuantity]):
    maybe_python_measurement = _python_measurement_option(target_unit, optional_net_quantity)
    return as_measurement(target_unit, maybe_python_measurement)


@singledispatch
@toolz.curry
def as_net_quantity(unknown, _measurement: om.Quantity) -> Optional[UnitsNet.IQuantity]:
    """
    Convert a .NET UnitsNet.IQuantity to a `pint` `Quantity` instance.

    This function is registered as the type-handler for the `object` type. In our situation, arriving here
    indicates an error by an implementer and so raises an error.

    Args:
        unknown: A parameter whose type is not expected.
        _measurement: The `Quantity` instance to convert.

    Returns:
        The equivalent `UnitsNet.IQuantity` instance.
    """
    raise TypeError(f'First argument, {unknown}, has type {type(unknown)}, unexpected by `as_net_quantity`.')


# noinspection PyUnresolvedReferences
_PINT_UNIT_CREATE_NET_UNITS = {
    om.registry.deg: UnitsNet.Angle.FromDegrees,
    om.registry.min: UnitsNet.Duration.FromMinutes,
    om.registry.ft_lb: UnitsNet.Energy.FromFootPounds,
    om.registry.J: UnitsNet.Energy.FromJoules,
    om.registry.lbf: UnitsNet.Force.FromPoundsForce,
    om.registry.N: UnitsNet.Force.FromNewtons,
    om.registry.ft: UnitsNet.Length.FromFeet,
    om.registry.m: UnitsNet.Length.FromMeters,
    om.registry.lb: UnitsNet.Mass.FromPounds,
    om.registry.kg: UnitsNet.Mass.FromKilograms,
    om.registry.hp: UnitsNet.Power.FromMechanicalHorsepower,
    om.registry.W: UnitsNet.Power.FromWatts,
    om.registry.psi: UnitsNet.Pressure.FromPoundsForcePerSquareInch,
    om.registry.kPa: UnitsNet.Pressure.FromKilopascals,
    om.registry.oil_bbl / om.registry.min: net_volume_flow_from_oil_bbl_per_min,
    ((om.registry.m ** 3) / om.registry.min): net_volume_flow_from_cu_m_per_min,
    om.registry.degF: UnitsNet.Temperature.FromDegreesFahrenheit,
    om.registry.degC: UnitsNet.Temperature.FromDegreesCelsius,
    om.registry.oil_bbl: UnitsNet.Volume.FromOilBarrels,
    (om.registry.m ** 3): UnitsNet.Volume.FromCubicMeters,
}


def _us_oilfield_slurry_rate(qv):
    return UnitsNet.Density.FromPoundsPerCubicFoot(qv)


# noinspection PyUnresolvedReferences
_PHYSICAL_QUANTITY_PINT_UNIT_NET_UNITS = {
    opq.PhysicalQuantity.DENSITY: {
        om.registry.lb / om.registry.cu_ft: _us_oilfield_slurry_rate,
        om.registry.lb / om.registry.ft ** 3: _us_oilfield_slurry_rate,
        om.registry.kg / (om.registry.m ** 3): UnitsNet.Density.FromKilogramsPerCubicMeter,
    },
    opq.PhysicalQuantity.PROPPANT_CONCENTRATION: {
        om.registry.lb / om.registry.gal: net_mass_concentration_from_lbs_per_gal,
        om.registry.kg / (om.registry.m ** 3): net_mass_concentration_from_kg_per_cu_m,
    },
}


# noinspection PyUnresolvedReferences
@as_net_quantity.register(opq.PhysicalQuantity)
@toolz.curry
def as_net_quantity_using_physical_quantity(physical_quantity,
                                            measurement: om.Quantity) -> Optional[UnitsNet.IQuantity]:
    """
    Convert a `Quantity` instance to a .NET `UnitsNet.IQuantity` instance.

    Args:
        physical_quantity: The `PhysicalQuantity`. Although we try to determine a unique mapping between units
        in `pint` and .NET `UnitsNet` units, we cannot perform a unique mapping for density and proppant
        concentration measured in the metric system (the units of both these physical quantities are
        "kg/m**3").
        measurement: The `Quantity` instance to convert.

    Returns:
        The equivalent `UnitsNet.IQuantity` instance.
    """
    if math.isnan(measurement.magnitude):
        return None

    quantity = UnitsNet.QuantityValue.op_Implicit(measurement.magnitude)
    if physical_quantity == opq.PhysicalQuantity.DENSITY:
        return toolz.get_in([physical_quantity, measurement.units], _PHYSICAL_QUANTITY_PINT_UNIT_NET_UNITS)(quantity)

    if physical_quantity == opq.PhysicalQuantity.PROPPANT_CONCENTRATION:
        return toolz.get_in([physical_quantity, measurement.units],
                            _PHYSICAL_QUANTITY_PINT_UNIT_NET_UNITS)(measurement.magnitude)

    if physical_quantity == opq.PhysicalQuantity.SLURRY_RATE:
        return toolz.get(measurement.units, _PINT_UNIT_CREATE_NET_UNITS)(measurement.magnitude)

    return toolz.get(measurement.units, _PINT_UNIT_CREATE_NET_UNITS)(quantity)


# noinspection PyUnresolvedReferences
@as_net_quantity.register(units.Common)
@toolz.curry
def as_net_quantity_using_common_units(to_common_unit, measurement: om.Quantity) -> Optional[UnitsNet.IQuantity]:
    """
    Convert a `Quantity` instance to a .NET `UnitsNet.IQuantity` instance corresponding `to_unit`.

    Args:
        to_common_unit: The target unit of measurement.
        measurement: The `Quantity` instance to convert.

    Returns:
        The equivalent `UnitsNet.IQuantity` instance.
    """
    # units.Common support no conversion so simply call another implementation.
    return as_net_quantity(to_common_unit.value.physical_quantity, measurement)


# noinspection PyUnresolvedReferences
@as_net_quantity.register(units.Metric)
@as_net_quantity.register(units.UsOilfield)
@toolz.curry
def as_net_quantity_in_specified_unit(specified_unit, measurement: om.Quantity) -> Optional[UnitsNet.IQuantity]:
    """
    Convert a `pint` `Quantity` to a .NET UnitsNet.IQuantity instance in a specified, but compatible unit.

    Args:
        specified_unit: The unit for the converted `Quantity` instance.
        measurement: The `Quantity` instance to convert.

    Returns:
        The equivalent `Quantity` instance in the specified unit.
    """
    target_measurement = measurement.to(specified_unit.value.unit)
    return as_net_quantity(specified_unit.value.physical_quantity, target_measurement)


def equal_net_quantities(left_quantity: UnitsNet.IQuantity, right_quantity: UnitsNet.IQuantity,
                         comparison_details: EqualsComparisonDetails = EqualsComparisonDetails()):
    """
    Compares two UnitsNet.IQuantity instances for equality

    Python.NET transforms == (perhaps indirectly) into a call to Equals. Unfortunately, comparing
    two measurements that have been transformed may have floating point differences. Specifically,
    UnitsNet marks the `Equals` method as `Obsolete` with the following message:
    > "It is not safe to compare equality due to using System.Double as the internal representation.
    > It is very easy to get slightly different values due to floating point operations. Instead use
    > Equals(Length, double, ComparisonType) to provide the max allowed absolute or relative error."

    Consequently, to determine if two `UnitsNet.IQuantity` instances are equal, I use the
    `Equals(Length, double, ComparisonType)` method applied to each instance.

    Args:
        left_quantity: The `IQuantity` instance on the "left-hand-side" of the (implicit) == operator.
        right_quantity: The `IQuantity` instance on the "right-hand-side" of the (implicit) == operator.
        comparison_details: The details of how to compare the two `UnitsNet.IQuantity` instances.

    Returns:

    """
    return left_quantity.Equals(right_quantity, comparison_details.tolerance, comparison_details.comparison_type)


def net_decimal_to_float(net_decimal: System.Decimal) -> float:
    """
    Convert a .NET Decimal value to a Python float.

    Python.NET currently leaves .NET values of type `Decimal` unconverted. For example, UnitsNet models units
    of the physical quantity, power, as values of type .NET 'QuantityValue` whose `Value` property returns a
    value of .NET `Decimal` type. This function assists in converting those values to Python values of type
    `float`.

    Args:
        net_decimal: The .NET `Decimal` value to convert.

    Returns:
        A value of type `float` that is "equivalent" to the .NET `Decimal` value. Note that this conversion is
        "lossy" because .NET `Decimal` values are exact, but `float` values are not.
    """
    return System.Decimal.ToDouble(net_decimal)


_UNIT_NET_UNITS = {
    units.Common.ANGLE: UnitsNet.Units.AngleUnit.Degree,
    units.Common.DURATION: UnitsNet.Units.DurationUnit.Minute,
    units.UsOilfield.DENSITY: UnitsNet.Units.DensityUnit.PoundPerCubicFoot,
    units.Metric.DENSITY: UnitsNet.Units.DensityUnit.KilogramPerCubicMeter,
    units.UsOilfield.ENERGY: UnitsNet.Units.EnergyUnit.FootPound,
    units.Metric.ENERGY: UnitsNet.Units.EnergyUnit.Joule,
    units.UsOilfield.FORCE: UnitsNet.Units.ForceUnit.PoundForce,
    units.Metric.FORCE: UnitsNet.Units.ForceUnit.Newton,
    units.UsOilfield.LENGTH: UnitsNet.Units.LengthUnit.Foot,
    units.Metric.LENGTH: UnitsNet.Units.LengthUnit.Meter,
    units.UsOilfield.MASS: UnitsNet.Units.MassUnit.Pound,
    units.Metric.MASS: UnitsNet.Units.MassUnit.Kilogram,
    units.UsOilfield.POWER: UnitsNet.Units.PowerUnit.MechanicalHorsepower,
    units.Metric.POWER: UnitsNet.Units.PowerUnit.Watt,
    units.UsOilfield.PRESSURE: UnitsNet.Units.PressureUnit.PoundForcePerSquareInch,
    units.Metric.PRESSURE: UnitsNet.Units.PressureUnit.Kilopascal,
    units.UsOilfield.PROPPANT_CONCENTRATION: UnitsNet.Units.MassConcentrationUnit.PoundPerUSGallon,
    units.Metric.PROPPANT_CONCENTRATION: UnitsNet.Units.MassConcentrationUnit.KilogramPerCubicMeter,
    units.UsOilfield.SLURRY_RATE: UnitsNet.Units.VolumeFlowUnit.OilBarrelPerMinute,
    units.Metric.SLURRY_RATE: UnitsNet.Units.VolumeFlowUnit.CubicMeterPerMinute,
    units.UsOilfield.TEMPERATURE: UnitsNet.Units.TemperatureUnit.DegreeFahrenheit,
    units.Metric.TEMPERATURE: UnitsNet.Units.TemperatureUnit.DegreeCelsius,
    units.UsOilfield.VOLUME: UnitsNet.Units.VolumeUnit.OilBarrel,
    units.Metric.VOLUME: UnitsNet.Units.VolumeUnit.CubicMeter,
}


@toolz.curry
def _convert_net_quantity_to_different_unit(target_unit: units.UnitSystem,
                                            net_quantity: UnitsNet.IQuantity) -> UnitsNet.IQuantity:
    """
    Convert one .NET `UnitsNet.IQuantity` to another .NET `UnitsNet.IQuantity` in a different unit `target_unit`
    Args:
        net_quantity: The `UnitsNet.IQuantity` instance to convert.
        target_unit: The unit to which to convert `maybe_net_quantity`.

    Returns:
        The .NET `UnitsNet.IQuantity` converted to `target_unit`.
    """
    result = net_quantity.ToUnit(_UNIT_NET_UNITS[target_unit])
    return result


def _net_decimal_to_float(net_decimal: System.Decimal) -> float:
    """
    Convert a .NET Decimal value to a Python float.

    Python.NET currently leaves .NET values of type `Decimal` unconverted. For example, UnitsNet models units
    of the physical quantity, power, as values of type .NET 'QuantityValue` whose `Value` property returns a
    value of .NET `Decimal` type. This function assists in converting those values to Python values of type
    `float`.

    Args:
        net_decimal: The .NET `Decimal` value to convert.

    Returns:
        A value of type `float` that is "equivalent" to the .NET `Decimal` value. Note that this conversion is
        "lossy" because .NET `Decimal` values are exact, but `float` values are not.
    """
    return System.Decimal.ToDouble(net_decimal)


_PHYSICAL_QUANTITY_NET_UNIT_PINT_UNITS = {
    opq.PhysicalQuantity.DENSITY: {
        UnitsNet.Units.DensityUnit.PoundPerCubicFoot: om.registry.lb / om.registry.ft ** 3,
        UnitsNet.Units.DensityUnit.KilogramPerCubicMeter: om.registry.kg / (om.registry.m ** 3),
    },
    opq.PhysicalQuantity.ENERGY: {
        UnitsNet.Units.EnergyUnit.FootPound: om.registry.ft_lb,
        UnitsNet.Units.EnergyUnit.Joule: om.registry.J,
    },
    opq.PhysicalQuantity.FORCE: {
        UnitsNet.Units.ForceUnit.PoundForce: om.registry.lbf,
        UnitsNet.Units.ForceUnit.Newton: om.registry.N,
    },
    opq.PhysicalQuantity.LENGTH: {
        UnitsNet.Units.LengthUnit.Foot: om.registry.ft,
        UnitsNet.Units.LengthUnit.Meter: om.registry.m,
    },
    opq.PhysicalQuantity.MASS: {
        UnitsNet.Units.MassUnit.Pound: om.registry.lb,
        UnitsNet.Units.MassUnit.Kilogram: om.registry.kg,
    },
    opq.PhysicalQuantity.POWER: {
        UnitsNet.Units.PowerUnit.MechanicalHorsepower: om.registry.hp,
        UnitsNet.Units.PowerUnit.Watt: om.registry.W,
    },
    opq.PhysicalQuantity.PRESSURE: {
        UnitsNet.Units.PressureUnit.PoundForcePerSquareInch: om.registry.psi,
        UnitsNet.Units.PressureUnit.Kilopascal: om.registry.kPa,
    },
    opq.PhysicalQuantity.PROPPANT_CONCENTRATION: {
        UnitsNet.Units.MassConcentrationUnit.PoundPerUSGallon: om.registry.lb / om.registry.gallon,
        UnitsNet.Units.MassConcentrationUnit.KilogramPerCubicMeter: om.registry.kg / om.registry.m ** 3,
    },
    opq.PhysicalQuantity.SLURRY_RATE: {
        UnitsNet.Units.VolumeFlowUnit.OilBarrelPerMinute: om.registry.oil_bbl / om.registry.min,
        UnitsNet.Units.VolumeFlowUnit.CubicMeterPerMinute: om.registry.m ** 3 / om.registry.min,
    },
    opq.PhysicalQuantity.TEMPERATURE: {
        UnitsNet.Units.TemperatureUnit.DegreeFahrenheit: om.registry.degF,
        UnitsNet.Units.TemperatureUnit.DegreeCelsius: om.registry.degC,
    },
    opq.PhysicalQuantity.VOLUME: {
        UnitsNet.Units.VolumeUnit.OilBarrel: om.registry.oil_bbl,
        UnitsNet.Units.VolumeUnit.CubicMeter: om.registry.m ** 3,
    },
}


def _to_pint_unit(physical_quantity: opq.PhysicalQuantity, net_unit: UnitsNet.Units) -> om.Unit:
    """
    Convert `net_unit`, a unit of measure for `physical_quantity`, to a `pint` unit.

    Args:
        physical_quantity: The physical quantity measured by `net_unit`.
        net_unit: The .NET UnitsNet.Unit to be converted.

    Returns:
        The `pint` Unit corresponding to `net_unit`.
    """
    result = toolz.get_in([physical_quantity, net_unit], _PHYSICAL_QUANTITY_NET_UNIT_PINT_UNITS)
    if result is not None:
        return result
    elif physical_quantity == opq.PhysicalQuantity.ANGLE:
        return om.registry.deg
    elif physical_quantity == opq.PhysicalQuantity.DURATION:
        return om.registry.min
