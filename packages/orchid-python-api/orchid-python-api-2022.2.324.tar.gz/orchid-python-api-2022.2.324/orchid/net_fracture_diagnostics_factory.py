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


import functools

import pendulum

from orchid import net_date_time as ndt

# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics import IFractureDiagnosticsFactory
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.Factories import FractureDiagnosticsFactory
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.Factories.ReferenceCounting import NullReferenceCounterFactory


@functools.lru_cache
def create() -> IFractureDiagnosticsFactory:
    """
    Return an instance of the fracture diagnostics factory used by .NET to construct DOM instances.

    >>> start = pendulum.parse('2022-02-23T15:53:23Z')
    >>> stop = pendulum.parse('2022-02-24T05:54:11Z')
    >>> net_start = ndt.as_net_date_time(start)
    >>> net_stop = ndt.as_net_date_time(stop)
    >>> factory = create()
    >>> date_time_offset_range = factory.CreateDateTimeOffsetRange(net_start, net_stop)
    >>> (date_time_offset_range.Start.ToString('o'), date_time_offset_range.Stop.ToString('o'))
    ('2022-02-23T15:53:23.0000000+00:00', '2022-02-24T05:54:11.0000000+00:00')

    Returns:
        An instance of the fracture diagnostics factory.
    """
    # TODO: We will need a "real" reference counter factory to support deleting DOM instances
    return FractureDiagnosticsFactory.Create(NullReferenceCounterFactory())


if __name__ == '__main__':
    import doctest
    doctest.testmod()
