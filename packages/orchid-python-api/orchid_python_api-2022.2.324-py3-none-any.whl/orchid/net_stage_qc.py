#  Copyright 2017-2022 Reveal Energy Services, Inc
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

"""
Expose constants to the Orchid Python API.

The .NET stage QC "class" implementation depends upon a number of constants. This module exposes those constants to the
Orchid Python API.
"""

import enum
import uuid

import toolz.curried as toolz

# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.Common import CorrectionStatus as NetCorrectionStatus


class CorrectionStatus(enum.Enum):
    # TODO: Change to use .NET `Enum` member.
    # Python.NET always transforms .NET `Enum` members into Python `int` values. This transformation is a known issue
    # (https://github.com/pythonnet/pythonnet/issues/1220). The Python.NET team has corrected the issue but only for
    # Python.NET 3.x; it has no plans for a backport.
    #
    # Although I have successfully use the Python.NET transformation of .NET `Enum` members to `ints`; I have
    # encountered issues with its usage in .NET `Variant` types which is used for stage QC information.
    #
    # To simplify the "work-around" implemented in `native_stage_qc_adapter`, I use the hard-coded string value of
    # .NET `CorrectionStatus`.
    #
    # See also the Jupyter notebook, `features/notebooks/explore_stage_qc.py`, for attempts to use the .NET `Enum`.
    CONFIRMED = 'Confirmed'
    NEW = 'New'
    UNCONFIRMED = 'Unconfirmed'


class StageQCTags(enum.Enum):
    QC_NOTES = 'stage_qc_notes'
    START_STOP_CONFIRMATION = 'stage_start_stop_confirmation'


def make_key(stage_id: uuid.UUID, tag: StageQCTags) -> str:
    return f'{str(stage_id)}|{tag.value}'


make_start_stop_confirmation_key = toolz.flip(make_key)(StageQCTags.START_STOP_CONFIRMATION)
make_qc_notes_key = toolz.flip(make_key)(StageQCTags.QC_NOTES)
