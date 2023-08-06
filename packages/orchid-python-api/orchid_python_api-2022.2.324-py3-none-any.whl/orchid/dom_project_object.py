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

import option

from orchid import dot_net_dom_access as dna


def transform_display_name(net_display_name):
    maybe_display_name = option.maybe(net_display_name)
    return maybe_display_name.expect('Unexpected value, `None`, for `display_name`.')


class DomProjectObject(dna.IdentifiedDotNetAdapter):
    name = dna.dom_property('name', 'The name of this data frame.')
    display_name = dna.transformed_dom_property('display_name', 'The display name of this data frame.',
                                                transform_display_name)
