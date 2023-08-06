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


import option

from orchid import (
    base,
    dot_net_dom_access as dna,
    dom_project_object as dpo,
    measurement as om,
    net_date_time as ndt,
    net_quantity as onq,
)


class NativeStagePartAdapter(dpo.DomProjectObject):
    def __init__(self, adaptee):
        super().__init__(adaptee, base.constantly(adaptee.Project))

    display_name_with_well = dna.dom_property('display_name_with_well',
                                              'The display stage number including the well name')
    display_name_without_well = dna.dom_property('display_name_without_well',
                                                 'The display stage number excluding the well name')
    part_no = dna.dom_property('part_number', 'The part number for this stage part')
    start_time = dna.transformed_dom_property('start_time', 'The start time of this stage part',
                                              ndt.as_date_time)
    stop_time = dna.transformed_dom_property('stop_time', 'The stop time of this stage part',
                                             ndt.as_date_time)

    @property
    def isip(self) -> om.Quantity:
        """
        Return the instantaneous shut-in pressure of this stage part in project units.
        """
        return onq.as_measurement(self.expect_project_units.PRESSURE, option.maybe(self.dom_object.Isip))
