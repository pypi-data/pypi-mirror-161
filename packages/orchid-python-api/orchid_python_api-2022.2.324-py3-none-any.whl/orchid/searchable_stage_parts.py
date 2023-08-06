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


from typing import Iterable, Optional


from orchid import (
    native_stage_part_adapter as spa,
    searchable_project_objects as spo,
)


class SearchableStageParts(spo.SearchableProjectObjects):
    def find_by_part_number(self, to_find: int) -> Optional[spa.NativeStagePartAdapter]:
        """
        Find a stage part with the specified part number.

        Args:
            to_find: The part number sought.

        Returns:
            The stage part with the specified part number.

            If no such stage part is found, returns `None`. If multiple stage parts with the specified part number are
            found, raises `spo.SearchableProjectMultipleMatchError`.
        """
        candidates = list(self.find(lambda s: s.part_no == to_find))
        if len(candidates) == 0:
            return None
        elif len(candidates) == 1:
            return candidates[0]
        else:
            raise spo.SearchableProjectMultipleMatchError(to_find)

    def find_by_display_name_with_well(self, to_find: str) -> Iterable[spa.NativeStagePartAdapter]:
        """
        Find a stage part with the specified display name with well.

        Args:
            to_find: The display name with well sought.

        Returns:
            The matching stage part(s).

            If no such stage part is in this collection, returns an empty iterator.
        """
        return self.find(lambda s: s.display_name_with_well == to_find)

    def find_by_display_name_without_well(self, to_find: str) -> Iterable[spa.NativeStagePartAdapter]:
        """
        Find a stage part without the specified display name with well.

        Args:
            to_find: The display name without well sought.

        Returns:
            The matching stage part(s).

            If no such stage part is in this collection, returns an empty iterator.
        """
        return self.find(lambda s: s.display_name_without_well == to_find)
