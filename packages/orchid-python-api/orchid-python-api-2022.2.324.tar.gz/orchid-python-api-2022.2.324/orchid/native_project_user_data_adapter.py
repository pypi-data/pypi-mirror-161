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

import json
from typing import Callable, Union
import uuid

import toolz.curried as toolz

from orchid import (
    dot_net_dom_access as dna,
    dot_net_disposable as dnd,
    net_stage_qc as nqc,
)


# noinspection PyUnresolvedReferences,PyPackageRequirements
from Orchid.FractureDiagnostics.Settings import IProjectUserData, Variant


class NativeProjectUserDataAdapter(dna.DotNetAdapter):
    """Adapts a .NET `IProjectUserData` instance to Python."""

    # TODO: Add code to `SdkAdapter` to allow handling `GetValue` and .NET `CorrectionStatus`
    # Python.NET has a [known issue](https://github.com/pythonnet/pythonnet/issues/1220) with its
    # handling of .NET Enum types. The Python.NET team has repaired this issue; however, the repair
    # is targeted for Python.NET 3. The team has specifically stated that they will *not* backport
    # this fix to the 2.5 version. Because .NET `CorrectionStatus` is a .NET `Enum` type, we
    # *cannot* construct a .NET `Variant` of type .NET `CorrectionStatus`.
    #
    # Our work-around for this issue is to implement this class in terms of the the JSON available
    # from the `IProjectUserData.ToJson`. This choice further requires hard-coding the logic used
    # by `StartStopTimeEditorViewModel` default `Variant` logic for QC notes and for start stop
    # confirmation.

    def __init__(self, adaptee: IProjectUserData):
        super().__init__(adaptee)

    def stage_qc_notes(self, stage_id: uuid.UUID) -> str:
        """
        Calculate the QC notes for the specified stage.

        Args:
            stage_id: The object ID of the stage of interest.

        Returns:
            The requested QC notes.
        """
        key_func = nqc.make_qc_notes_key
        transform_func = toolz.identity
        default_result = ''

        return self._extract_value_for_stage_id(stage_id, key_func, default_result, transform_func)

    def stage_start_stop_confirmation(self, stage_id: uuid.UUID) -> nqc.CorrectionStatus:
        """
        Calculate the start stop confirmation for the specified stage.

        Args:
            stage_id: The object ID of the stage of interest.

        Returns:
            The requested start stop confirmation.
        """
        key_func = nqc.make_start_stop_confirmation_key
        transform_func = nqc.CorrectionStatus
        default_result = nqc.CorrectionStatus.NEW

        return self._extract_value_for_stage_id(stage_id, key_func, default_result, transform_func)

    def _extract_value_for_stage_id(self,
                                    stage_id: uuid.UUID,
                                    key_func: Callable[[uuid.UUID], str],
                                    default_result: Union[str, nqc.CorrectionStatus],
                                    transform_func: Callable[[str], Union[str, nqc.CorrectionStatus]]):
        project_user_data_json = json.loads(self.dom_object.ToJson())
        confirmation_key = key_func(stage_id)
        # TODO: Replace hard-coded "copy" of logic
        # Hard-coded logic for QC notes default value from `StartStopTimeEditorViewModel`:
        # return .NET `CorrectionStatus.New` if either of stage ID or of start stop
        # confirmation is unavailable.
        result = default_result
        if confirmation_key in project_user_data_json:
            actual_value_type = toolz.get_in([confirmation_key, 'Type'], project_user_data_json)
            assert actual_value_type == 'System.String', (f'Expected, "System.String",'
                                                          f' but found "{actual_value_type}".')
            text_status = toolz.get_in([confirmation_key, 'Value'], project_user_data_json)
            result = transform_func(text_status)
        return result

    def set_stage_qc_notes(self, stage_id: uuid.UUID, to_notes: str) -> None:
        """
        Set the stage QC notes `to_notes` for the specified stage.
        Args:
            stage_id: The object ID that identifies the stage of interest.
            to_notes: The value to which to set the stage QC notes.
        """
        self._set_value(stage_id, nqc.make_qc_notes_key, to_notes, toolz.identity)

    def set_stage_start_stop_confirmation(self, stage_id: uuid.UUID,
                                          to_confirmation: nqc.CorrectionStatus) -> None:
        """
        Set the stage start stop confirmation `to_confirmation` for the specified stage.

        Args:
            stage_id: The object ID that identifies the stage of interest.
            to_confirmation: The value to which to set the stage start stop confirmation.
        """
        self._set_value(stage_id, nqc.make_start_stop_confirmation_key, to_confirmation, lambda v: v.value)

    def _set_value(self, stage_id, key_func, to_value, value_func):
        """
        Invoke `SetValue` on the mutable DOM object.

        Args:
            stage_id: The object ID identifying the stage whose value is to be set.
            key_func: A callable that generates the key identifying the value.
            to_value: The value to set.
            value_func: A function transforming the value to the appropriate .NET value.
        """
        with dnd.disposable(self.dom_object.ToMutable()) as mutable_pud:
            mutable_pud.SetValue(key_func(stage_id),
                                 Variant.Create.Overloads[str](value_func(to_value)))
