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
from toolz import curried as toolz


def constantly(x):
    """
    Creates a function that always returns the value, `x`, independent of **all** arguments passed to it..
    Args:
        x: The value to return

    Returns:
        Returns a function takes any arguments yet always returns `x`.
    """

    # noinspection PyUnusedLocal
    def make_constantly(*args, **kwargs):
        return toolz.identity(x)

    return make_constantly
