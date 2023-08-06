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


import abc
from typing import Union

import toolz.curried as toolz
import option

from orchid import (
    dot_net_dom_access as dna,
    net_quantity as onq,
    unit_system as units,
)

# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics import ISubsurfacePoint


class SubsurfacePoint(dna.IdentifiedDotNetAdapter):
    """An abstract base class for subsurface points."""

    def __init__(self, adaptee: ISubsurfacePoint, target_length_unit: Union[units.UsOilfield, units.Metric]):
        """
        Construct an instance adapting `adaptee` so that all lengths are expressed in `target_length_unit`.

        Args:
            adaptee: The .NET `ISubsurfacePoint` being adapted.
            target_length_unit: The target unit for all lengths.
        """
        super().__init__(adaptee)
        self._as_length_measurement_func = onq.as_measurement(target_length_unit)

    depth_origin = dna.dom_property('depth_datum',
                                    'The datum or origin for the z-coordinate of this point.')
    xy_origin = dna.dom_property('well_reference_frame_xy',
                                 'The reference frame or origin for the x-y coordinates of this point.')

    @property
    def x(self):
        """The x-coordinate of this point."""
        return self._as_length_measurement_func(option.maybe(self.dom_object.X))

    @property
    def y(self):
        """The y-coordinate of this point."""
        return self._as_length_measurement_func(option.maybe(self.dom_object.Y))

    @property
    def depth(self):
        """The depth of this point."""
        return self._as_length_measurement_func(option.maybe(self.dom_object.Depth))


@toolz.curry
def make_subsurface_point(target_unit: Union[units.UsOilfield, units.Metric],
                          net_subsurface_point: ISubsurfacePoint) -> SubsurfacePoint:
    return SubsurfacePoint(net_subsurface_point, target_unit)
