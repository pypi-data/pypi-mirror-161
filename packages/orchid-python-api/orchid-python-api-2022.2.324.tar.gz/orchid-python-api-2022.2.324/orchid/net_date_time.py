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

"""
Functions to convert between .NET `DateTime` and similar instances and Python `pendulum` instances.
"""


import datetime as dt
import enum
import functools
from typing import Tuple, Union

import dateutil.tz as duz
import pendulum as pdt
import pendulum.tz as ptz

from orchid import base

# noinspection PyUnresolvedReferences,PyPackageRequirements
from System import (DateTime, DateTimeKind, DateTimeOffset, TimeSpan)


# Encapsulate the use of pendulum and DateTime.
UTC = pdt.UTC
NET_NAT = DateTime.MinValue
NAT = pdt.DateTime.min


class TimePointTimeZoneKind(enum.Enum):
    """Models the kind of time point.

    This class eases conversions to the .NET `DateTime` class by providing Python with similar capabilities as
    the .NET `Enum`. (See
    [DateTimeKind](https://docs.microsoft.com/en-us/dotnet/api/system.datetimekind?view=net-5.0) for details).
    """
    UTC = DateTimeKind.Utc  # Time zone is UTC
    LOCAL = DateTimeKind.Local  # Time zone is specified to be local
    UNSPECIFIED = DateTimeKind.Unspecified  # Time zone is unspecified


class NetDateTimeError(ValueError):
    """
    Raised when an error occurs accessing the .NET `TimeZoneInfo` of a .NET `DateTime` instance.
    """
    pass


class NetDateTimeLocalDateTimeKindError(NetDateTimeError):
    """
    Raised when the `DateTime.Kind` property of a .NET `DateTime` instance is `DateTimeKind.Local`.
    """
    def __init__(self, net_time_point: Union[DateTime, DateTimeOffset]):
        """
        Construct an instance from a .NET DateTime point in time.

        Args:
            net_time_point: A .NET DateTime representing a specific point in time.
        """
        super().__init__(self, '.NET DateTimeKind cannot be Local.', net_time_point.ToString("O"))


class NetDateTimeUnspecifiedDateTimeKindError(NetDateTimeError):
    """
    Raised when the `DateTimeKind` property of a .NET `DateTime` instance is not recognized.
    """
    ERROR_PREFACE = '.NET DateTimeKind is unexpectedly Unspecified.'

    ERROR_SUFFIX = """
    Although .NET DateTime.Kind should not be Unspecified, it may be
    safe to ignore this error by catching the exception.

    However, because it unexpected, **please** report the issue to
    Reveal Energy Services. 
    """

    def __init__(self, net_time_point: Union[DateTime, DateTimeOffset]):
        """
        Construct an instance from a .NET DateTime point in time.

        Args:
            net_time_point: A .NET DateTime representing a specific point in time.
        """
        super().__init__(self, NetDateTimeUnspecifiedDateTimeKindError.ERROR_PREFACE,
                         net_time_point.ToString("O"), NetDateTimeUnspecifiedDateTimeKindError.ERROR_SUFFIX)


class NetDateTimeNoTzInfoError(NetDateTimeError):
    """
    Raised when the `DateTimeKind` property of a .NET `DateTime` instance is
    `DateTimeKind.Unspecified`.
    """
    def __init__(self, time_point):
        """
        Construct an instance from a Python point in time.

        Args:
            time_point: A `pdt.DateTime` representing a specific point in time.
        """
        super().__init__(self, f'The Python time point must specify the time zone.', time_point.isoformat())


class NetDateTimeOffsetNonZeroOffsetError(NetDateTimeError):
    """
    Raised when the `Offset` property of a .NET `DateTimeOffset` is non-zero.
    """
    def __init__(self, net_date_time_offset):
        """
        Construct an instance from a .NET `DateTimeOffset`.

        Args:
            net_date_time_offset: A .NET `DateTimeOffset` representing a specific point in time.
        """
        super().__init__(self,
                         f'The `Offset` of the .NET `DateTimeOffset`, {net_date_time_offset.ToString("o")},'
                         ' cannot be non-zero.')


@functools.singledispatch
def as_date_time(net_time_point: object) -> pdt.DateTime:
    raise NotImplementedError


@as_date_time.register(type(None))
def _(net_time_point) -> pdt.DateTime:
    """
    Convert a .NET `DateTime` instance to a `pdt.DateTime` instance.

    Args:
        net_time_point: A point in time of type .NET `DateTime`.

    Returns:
        The `pdt.DateTime` equivalent to the `to_test`.

        If `net_time_point` is `DateTime.MaxValue`, returns `pdt.DateTime.max`. If `net_time_point` is
        `DateTime.MinValue`, returns `DATETIME_NAT`.
    """
    return NAT


@as_date_time.register
def _(net_time_point: DateTime) -> pdt.DateTime:
    """
    Convert a .NET `DateTime` instance to a `pdt.DateTime` instance.

    Args:
        net_time_point: A point in time of type .NET `DateTime`.

    Returns:
        The `pdt.DateTime` equivalent to the `to_test`.

        If `net_time_point` is `DateTime.MaxValue`, returns `pdt.DateTime.max`. If `net_time_point` is
        `DateTime.MinValue`, returns `DATETIME_NAT`.
    """
    if net_time_point == DateTime.MaxValue:
        return pdt.DateTime.max

    if net_time_point == DateTime.MinValue:
        return NAT

    if net_time_point.Kind == DateTimeKind.Utc:
        return _net_time_point_to_datetime(base.constantly(ptz.UTC), net_time_point)

    if net_time_point.Kind == DateTimeKind.Unspecified:
        raise NetDateTimeUnspecifiedDateTimeKindError(net_time_point)

    if net_time_point.Kind == DateTimeKind.Local:
        raise NetDateTimeLocalDateTimeKindError(net_time_point)

    raise ValueError(f'Unknown .NET DateTime.Kind, {net_time_point.Kind}.')


@as_date_time.register
def _(net_time_point: DateTimeOffset) -> pdt.DateTime:
    """
    Convert a .NET `DateTimeOffset` instance to a `pdt.DateTime` instance.

    Args:
        net_time_point: A point in time of type .NET `DateTimeOffset`.

    Returns:
        The `pdt.DateTime` equivalent to the `net_time_point`.
    """
    if net_time_point == DateTimeOffset.MaxValue:
        return pdt.DateTime.max

    if net_time_point == DateTimeOffset.MinValue:
        return NAT

    def net_date_time_offset_to_timezone(ntp):
        integral_offset = int(ntp.Offset.TotalSeconds)
        if integral_offset == 0:
            return ptz.UTC

        return ptz.timezone(integral_offset)

    return _net_time_point_to_datetime(net_date_time_offset_to_timezone, net_time_point)


def as_net_date_time(time_point: pdt.DateTime) -> DateTime:
    """
    Convert a `pdt.DateTime` instance to a .NET `DateTime` instance.

    Args:
        time_point: The `pdt.DateTime` instance to covert.

    Returns:
        The equivalent .NET `DateTime` instance.

        If `time_point` is `pdt.DateTime.max`, return `DateTime.MaxValue`. If `time_point` is
        `DATETIME_NAT`, return `DateTime.MinValue`.
    """
    if time_point == pdt.DateTime.max:
        return DateTime.MaxValue

    if time_point == NAT:
        return DateTime.MinValue

    if not time_point.tzinfo == ptz.UTC:
        raise NetDateTimeNoTzInfoError(time_point)

    carry_seconds, milliseconds = microseconds_to_milliseconds_with_carry(time_point.microsecond)
    result = DateTime(time_point.year, time_point.month, time_point.day,
                      time_point.hour, time_point.minute, time_point.second + carry_seconds,
                      milliseconds, DateTimeKind.Utc)
    return result


def as_net_date_time_offset(time_point: pdt.DateTime) -> DateTimeOffset:
    """
    Convert a `pdt.DateTime` instance to a .NET `DateTimeOffset` instance.

    Args:
        time_point: The `pdt.DateTime` instance to covert.

    Returns:
        The equivalent .NET `DateTimeOffset` instance.

        If `time_point` is `pdt.DateTime.max`, return `DateTime.MaxValue`. If `time_point` is
        `DATETIME_NAT`, return `DateTime.MinValue`.
    """
    if time_point == pdt.DateTime.max:
        return DateTimeOffset.MaxValue

    if time_point == NAT:
        return DateTimeOffset.MinValue

    date_time = as_net_date_time(time_point)
    result = DateTimeOffset(date_time)
    return result


def as_net_time_span(to_convert: pdt.Duration):
    """
    Convert a `pdt.Duration` instance to a .NET `TimeSpan`.

    Args:
        to_convert: The `pdt.Duration` instance to convert.

    Returns:
        The .NET `TimeSpan` equivalent to `to_convert`.
    """
    return TimeSpan(round(to_convert.total_seconds() * TimeSpan.TicksPerSecond))


def as_duration(to_convert: TimeSpan) -> pdt.Duration:
    """
    Convert a .NET `TimeSpan` to a python `pdt.Duration`

    Args:
        to_convert: The .NET `TimeSpan` to convert.

    Returns:
        The `pdt.Duration` equivalent to `to_convert`.

    """
    return pdt.duration(seconds=to_convert.TotalSeconds)


def as_time_delta(net_time_span: TimeSpan):
    """
    Convert a .NET `TimeSpan` to a Python `dt.timedelta`.

    Args:
        net_time_span: The .NET `TimeSpan` to convert.

    Returns:
        The equivalent dt.time_delta value.

    """
    return dt.timedelta(seconds=net_time_span.TotalSeconds)


def microseconds_to_milliseconds_with_carry(to_convert: int) -> Tuple[int, int]:
    """
    Convert microseconds to an integral number of milliseconds with a number of seconds to carry.

    Args:
        to_convert: The microseconds to convert.

    Returns:
        A tuple of the form, (number of seconds to "carry",  number of the integral milliseconds).
    """

    raw_milliseconds = round(to_convert / 1000)
    return divmod(raw_milliseconds, 1000)


def is_utc(time_point):
    return (time_point.tzinfo == pdt.UTC or
            time_point.tzinfo == dt.timezone.utc or
            time_point.tzinfo == duz.UTC)


def _net_time_point_to_datetime(time_zone_func, net_time_point):
    return pdt.datetime(net_time_point.Year, net_time_point.Month, net_time_point.Day,
                        net_time_point.Hour, net_time_point.Minute, net_time_point.Second,
                        net_time_point.Millisecond * 1000, tz=time_zone_func(net_time_point))
