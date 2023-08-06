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

# We must use IntEnum for accurate comparison in testing because PythonNet converts .NET enum values to integers.
from enum import IntEnum

# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics import WellReferenceFrameXy as NetWellReferenceFrameXy
# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics import DepthDatum as NetDepthDatum


class WellReferenceFrameXy(IntEnum):
    ABSOLUTE_STATE_PLANE = NetWellReferenceFrameXy.AbsoluteStatePlane
    PROJECT = NetWellReferenceFrameXy.Project
    WELL_HEAD = NetWellReferenceFrameXy.WellHead


class DepthDatum(IntEnum):
    GROUND_LEVEL = NetDepthDatum.GroundLevel
    KELLY_BUSHING = NetDepthDatum.KellyBushing
    SEA_LEVEL = NetDepthDatum.SeaLevel
