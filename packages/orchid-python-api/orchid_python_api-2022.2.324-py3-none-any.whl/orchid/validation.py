#  Copyright (c) 2017-2022 Reveal Energy Services, Inc 
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

"""This module contains common functions used to validate arguments."""


from orchid import (unit_system as units)


def arg_not_none(_, arg) -> bool:
    """
    Tests if the single argument is not None

    :param _: Ignored (typically mapped to `self` for bound methods)
    :param arg: The argument to be tested
    :return: True if arg is not None; otherwise, false.
    """
    return arg is not None


def arg_neither_empty_nor_all_whitespace(_, arg: str) -> bool:
    """
    Tests if the single argument is not None

    :param _: Ignored (typically mapped to `self` for bound methods)
    :param arg: The argument to be tested
    :return: True if arg is neither an empty string nor a string consisting only of whitespace.
    """
    return len(arg.strip()) > 0


def arg_is_acceptable_pressure_unit(_, target_unit):
    return (target_unit == units.UsOilfield.PRESSURE) or (target_unit == units.Metric.PRESSURE)


def is_unit_system_length(unit_to_test):
    return unit_to_test == units.UsOilfield.LENGTH or unit_to_test == units.Metric.LENGTH

