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

from orchid import searchable_project_objects as spo


class SearchableStages(spo.SearchableProjectObjects):
    def find_by_display_stage_number(self, to_find: int):
        candidates = list(self.find(lambda s: s.display_stage_number == to_find))
        if len(candidates) == 0:
            return None
        elif len(candidates) == 1:
            return candidates[0]
        else:
            raise spo.SearchableProjectMultipleMatchError(to_find)

    def find_by_display_name_with_well(self, to_find: str):
        return self.find(lambda s: s.display_name_with_well == to_find)
