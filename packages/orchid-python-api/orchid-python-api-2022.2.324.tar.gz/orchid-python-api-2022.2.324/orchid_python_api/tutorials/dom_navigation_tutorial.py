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

# Tutorial DOM walk-through

"""
This script illustrates navigating a loaded project using the Orchid* Python API.

(*Orchid is a mark of Reveal Energy Services, Inc)
"""

# 0.5 Import packages

# The only import needed for the Python API is `orchid` itself.
import orchid

# Import other packages to meet specific needs
from dataclasses import dataclass  # Used to format DOM object data for readability
import pprint  # Used to "pretty-print" complex data, for example, lists
import textwrap  # Help to format pretty printed text
import uuid  # Used to construct an object ID from its string representation


# These functions and classes exists simply to assist in executing this script.


def banner(banner_text):
    print(len(banner_text) * '=')
    print(banner_text)
    print(len(banner_text) * '=')
    print()


def pretty_print_with_header(items, header):
    header_text = f'{header} returns:'
    pretty_printed_text = (textwrap
                           .TextWrapper(initial_indent=2 * ' ', subsequent_indent=(2 + 1) * ' ')
                           .fill(f'{pprint.pformat(items)}'))
    text_to_print = f'{header_text}\n{pretty_printed_text}'
    print(text_to_print)
    print()


def wait_for_input():
    input('Press enter to continue...')
    print()


@dataclass
class AboutProjectObject:
    """Class used to conveniently and consistently print project object identifying information."""
    name: str
    display_name: str
    object_id: uuid.UUID

    def __init__(self, project_object):
        self.name = project_object.name
        self.display_name = project_object.display_name
        self.object_id = project_object.object_id


@dataclass
class AboutStage(AboutProjectObject):
    """Specialized class for consistently and conveniently printing stage information."""
    display_stage_number: int = 0
    display_name_with_well: str = ''

    def __init__(self, stage):
        super().__init__(stage)
        self.display_stage_number = stage.display_stage_number
        self.display_name_with_well = stage.display_name_with_well


def navigate_dom():
    # 1.0 Load the .ifrac project

    # The following code simply captures the configured location of the Orchid training data. It is not
    # needed to use the Orchid Python API itself, but it is used in this example to load a well-known
    # `.ifrac` file.
    orchid_training_data_path = orchid.training_data_path()

    project = orchid.load_project(str(orchid_training_data_path.joinpath('frankNstein_Bakken_UTM13_FEET.ifrac')))

    # Our project is now loaded in memory. An Orchid project has many collections of other items. For
    # example, a project has a collection of wells, and a well has a collection of stages.
    #
    # Each of these objects, for example, each well and each stage, is identified by a unique identifier (an
    # instance of `uuid.UUID`). However, these identifiers, in order to be unique, are **not** easily
    # remembered by people. Further, Orchid **does not** require that alternatives, like a well name or
    # display name, be unique. To allow for convenient searching, project objects like wells and stages are
    # kept in a `SearchableProjectObjects` collection. This class provides methods for searching for more
    # specific instances:
    #
    # - `find_by_object_id()` - Returns the matching object or `None` if no such object exists
    # - `find_by_name()` - Returns an **iterator** of matching objects (since more than one may match).
    # - `find_by_display_name()` - Returns an **iterator** of matching objects.
    #
    # It provides methods returning all valid values of these keys:
    #
    # - `all_object_ids()`
    # - `all_names()`
    # - `all_display_names()`
    #
    # Since `find_by_object_id()`, `find_by_name()` and `find_by_display_name()` do not exhaust the criteria
    # you might want to use to find objects of interest, we have included a more generic method, `find()`,
    # that takes a predicate (a callable) and returns an iterator over all objects for which the predicate
    # returns `True`.
    #
    # Finally, we provide the general ability to iterate over all project objects using two mechanisms. The
    # older mechanism is the `all_objects()` method that returns an iterator over all objects in the
    # collection.
    #
    # Beginning with version 2021.3.318 of the Orchid Python API, we have made `SearchableProjectObjects` an
    # iterator. This change allows one to use the very familiar Python idiom of:
    #
    # ```
    # for well in projects.wells():
    #     // processing
    #     for a single well
    # ```
    #
    # Additionally, one can use `SearchableProjectObjects` in list, dictionary and generator expressions. For
    # example, to create a dictionary of wells keyed by the well object ID (since ** only ** object ID is
    # guaranteed to be unique) one would write:
    #
    # ```
    # wells_by_id = {well.object_id: well for well in project.wells()}
    # ```
    #
    # Using `SearchableProjectObjects` as an iterator is very general, is easily understood, and is most
    # useful when exploring a project interactively at a REPL. However, we have seen that using this general
    # technique easily leads to duplicated code to search through the collection of project objects for the
    # specific object that you actually need for your application. Consequently, we encourage you to use the
    # query methods of `SearchableProjectObjects`, including the general `find(...)` methods, first. If those
    # do not meet your needs, please let us know by creating
    # [an issue](https://github.com/Reveal-Energy-Services/orchid-python-api/issues).

    # 2.0 Query well "keys"

    # Particularly during exploration of a project, you may not know the specific object in which you are
    # interested, but you know something about its name or its display name. The Orchid Python API provides
    # you with the `all_names()` and `all_display_names()` to iterate over those names.

    banner('Query well identifying information: name, display name and object ID')

    all_well_names = list(project.wells().all_names())
    pretty_print_with_header(all_well_names, 'list(project.wells().all_names())')

    all_well_display_names = list(project.wells().all_display_names())
    pretty_print_with_header(all_well_display_names, 'list(project.wells().all_display_names())')

    # 2.1 Query all object ids

    # For completeness, we provide the `all_object_ids()` to list all the object IDs.
    all_well_object_ids = list(project.wells().all_object_ids())
    pretty_print_with_header(all_well_object_ids, 'list(project.wells().all_display_names())')

    wait_for_input()

    # 3.0 Find well by "key"

    banner('Find a collection of wells using name and display name')

    # The method, `find_by_name()`, returns an iterable over wells.
    wells_of_interest_by_name = list(project.wells().find_by_name('Demo_1H'))
    pretty_print_with_header([AboutProjectObject(well) for well in wells_of_interest_by_name],
                             'list(project.wells().find_by_name("Demo_1H"))')

    # Similarly, the method, `find_by_display_name()`, returns an iterable over wells
    wells_of_interest_by_display_name = list(project.wells().find_by_display_name('Demo_2H'))
    pretty_print_with_header([AboutProjectObject(well) for well in wells_of_interest_by_name],
                             'list(project.wells().find_by_display_name("Demo_1H"))')

    wait_for_input()

    # Because `find_by_name()` and `find_by_display_name()` returns an **iterator**, one typically must handle
    # this method returning
    #
    # - An empty iterator
    # - An iterator with more than 1 item
    # - An iterator with a single item
    #
    # For example,
    banner('One must handle the three possibilities of zero, one or many wells')

    well_name_of_interest = 'Demo_3H'
    wells_of_interest_by_name = list(project.wells().find_by_name(well_name_of_interest))
    if len(wells_of_interest_by_name) == 0:
        print(f'No well in project with name, {well_name_of_interest}')
        print()
    elif len(wells_of_interest_by_name) > 1:
        print(f'Found {len(wells_of_interest_by_name)} wells in project with name,'
              f' {well_name_of_interest}')
        print()
    else:
        pretty_print_with_header(AboutProjectObject(wells_of_interest_by_name[0]),
                                 f'project.wells().find_by_name({well_name_of_interest}) '
                                 f'finds single well')

    # Another way to handle multiple wells found by `find_by_name()` is to use `assert` statements. This way
    # is suitable if any number of matches other than one is an error.

    banner('Or one must use `assert` if not finding a single well is an error')

    assert len(wells_of_interest_by_name) == 1, (f'Expected one well with name, {well_name_of_interest},'
                                                 f' but found {len(wells_of_interest_by_display_name)}')
    well_of_interest = wells_of_interest_by_name[0]
    pretty_print_with_header(f'Assert single well with name, {well_name_of_interest}, in project\n'
                             f'  {AboutProjectObject(wells_of_interest_by_name[0])}',
                             f'project.wells().find_by_name({well_name_of_interest})')

    wait_for_input()

    banner('But one can find a single well using object ID')

    # However, `find_by_object_id()` method returns either a well with the specified object ID or None.
    #
    # If a well with this object ID exists:
    object_id = '9fe727b0-5fd1-4240-b475-51c1363edb0d'
    well_of_interest_by_object_id = project.wells().find_by_object_id(uuid.UUID(object_id))
    pretty_print_with_header((AboutProjectObject(well_of_interest_by_object_id)
                              if well_of_interest_by_object_id is not None
                              else "No such object"),
                             f'project.wells().find_by_object_id(uuid.UUID({object_id})')

    # But if no well with this object ID exists:
    banner('Remember that searching by object ID may return `None`')
    object_id = '00000000-0000-0000-0000-000000000000'
    well_of_interest_by_object_id = project.wells().find_by_object_id(uuid.UUID(object_id))
    well_of_interest = (AboutProjectObject(well_of_interest_by_object_id)
                        if well_of_interest_by_object_id is not None
                        else "No such object.")
    pretty_print_with_header(well_of_interest, f'project.wells().find_by_object_id(uuid.UUID({object_id})')

    wait_for_input()

    # 4.0 The `find()` method supports more generic queries

    banner('Use the "generic" `find` method with a predicate to find other wells of interest')

    # The `find()` method returns an iterable over the wells for which the specified predicate is `True`
    wells_of_interest = list(
        project.wells().find(lambda well: well.name == 'Demo_3H' or well.name == 'Demo_4H'))
    pretty_print_with_header([AboutProjectObject(well) for well in wells_of_interest],
                             'list(project.wells().find(<some condition(s)>))')

    wait_for_input()

    # 5.0 Finally, if you wish to iterate over all wells, use the `all_objects()` method

    banner('The Orchid Python API provides two mechanisms to iterate over items in `SearchableProjectObjects')

    banner('The `all_objects` method returns an iterator over all project objects in the collection')

    # The method, `all_objects()`, returns an iterable over **all** wells in the project
    wells_of_interest = list(project.wells().all_objects())
    pretty_print_with_header([AboutProjectObject(well) for well in wells_of_interest],
                             'list(project.wells().all_objects()')

    wait_for_input()

    banner('The `SearchableProjectObjects` class is an iterator over all project objects in the collection')

    # The `SearchableProjectObjects` class is an iterator and supports typical Python iterator idioms like:
    pretty_print_with_header([AboutProjectObject(well) for well in project.wells()],
                             'project.wells() returns a Python iterator')

    wait_for_input()

    # All the project top-level objects provide a similar interface:
    #
    # - `project.data_frames()`
    # - `project.monitors()`
    # - `project.time_series()`
    # - `project.wells()`
    #

    banner('All top-level project objects provide a similar interface')
    for top_level_name in ['Data frames',
                           'Monitors',
                           'Time series',
                           'Wells']:
        print(f'- {top_level_name}')
    print()

    wait_for_input()

    # Stages have the same interface; however, stages also have two additional methods:
    #
    # - `stage.find_by_display_stage_number()`
    # - `stage.find_by_display_name_with_well()`

    banner('Stages have two additional methods for searching')

    # 6.0 Additional `SearchableStages` methods

    # 6.1 Find stages with a specific display stage number

    banner('One can find a specific stage with a display stage number')

    # The method, `find_by_display_stage_number()`, returns either the single stage with the display
    # stage number or it returns `None`.
    #
    # Begin by searching for the well of interest.
    well_display_name_of_interest = 'Demo_1H'
    wells_of_interest_by_display_name = [
        well for well in project.wells().find_by_display_name(well_display_name_of_interest)
    ]

    assert len(wells_of_interest_by_display_name) == 1, \
        f'Expected one well with display_name, {well_display_name_of_interest},' \
        f' but found {len(wells_of_interest_by_display_name)}'
    well_of_interest = wells_of_interest_by_display_name[0]

    # Now search for a stage with a specified display stage number.
    stage_display_number_of_interest = 7
    stage_of_interest = well_of_interest.stages().find_by_display_stage_number(stage_display_number_of_interest)
    if stage_of_interest is not None:
        pretty_print_with_header(AboutStage(stage_of_interest),
                                 f'well_of_interest.stages().'
                                 f'find_by_display_stage_number({stage_display_number_of_interest})')
    else:
        print(f'No stage with display stage number, {stage_display_number_of_interest}.')

    banner('But again, searching by a display stage number may return `None`')

    # If you search for a stage by display stage number that does **not** exist:
    stage_display_number_of_interest = 9999
    stage_of_interest = well_of_interest.stages().find_by_display_stage_number(stage_display_number_of_interest)
    if stage_of_interest is not None:
        pretty_print_with_header(AboutStage(stage_of_interest),
                                 f'well_of_interest.stages().'
                                 f'find_by_display_stage_number({stage_display_number_of_interest})')
    else:
        print(f'No stage with display stage number, {stage_display_number_of_interest}.')

    wait_for_input()

    # 6.2 Find stages with a specific display name with well

    banner('One can find a collection of stages with a specified `display_name_with_well`')

    # The method, `find_by_display_name_with_well()`, returns:
    #
    # - An empty iterator if no stage with the specified display name with well exists
    # - An iterator with a single item if exactly one stage with the specified display name with well exists
    # - An iterator with multiple items if many stages with the specified display name with well exists
    #
    # For example, begin by searching for a well of interest.
    well_name_of_interest = 'Demo_2H'
    wells_of_interest_by_name = list(project.wells().find_by_name(well_name_of_interest))
    assert len(wells_of_interest_by_name) == 1, (f'Expected one well with name, {well_name_of_interest},'
                                                 f' but found {len(wells_of_interest_by_display_name)}')
    well_of_interest = wells_of_interest_by_name[0]

    stage_display_name_with_well_of_interest = 'Demo_2H-Stage-14'
    stages_of_interest = [AboutStage(stage) for stage
                          in well_of_interest.stages().find_by_display_name_with_well
                          (stage_display_name_with_well_of_interest)]
    pretty_print_with_header(stages_of_interest,
                             f'list(well_of_interest.stages().find_by_display_name_with_well'
                             f'({stage_display_name_with_well_of_interest})')

    banner('One must handle the three possibilities of zero, one or many stages')

    if len(stages_of_interest) == 0:
        print(f'No stage in well, {well_of_interest.display_name}, in project with name, '
              f'{stage_display_name_with_well_of_interest}')
        print()
    elif len(stages_of_interest) > 1:
        print(f'Found {len(stages_of_interest)} stages in well,'
              f' {well_of_interest.display_name}, with display name with well,'
              f' {stage_display_name_with_well_of_interest}')
        print(0)
    else:
        pretty_print_with_header(AboutStage(stages_of_interest[0]),
                                 f'project.wells().find_by_name({stage_display_name_with_well_of_interest}) '
                                 f'finds single stage')

    print()

    # Another way to handle multiple stages found by `find_by_display_name_with_well()` is to use `assert`
    # statements. This way is suitable if any number of matches other than one is an error.

    banner('Or one must use `assert` if not finding a single stage is an error')

    assert len(stages_of_interest) == 1, \
        (f'Expected one well with name, ' f'{stage_display_name_with_well_of_interest},'
         f' but found {len(stages_of_interest)}')
    stage_of_interest = stages_of_interest[0]

    print(AboutStage(stage_of_interest))

    wait_for_input()


def main():
    print(__doc__)
    navigate_dom()


if __name__ == '__main__':
    main()
