# -*- coding: utf-8 -*-

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


from typing import Optional

import deal
import option

from orchid.project import Project
from orchid.project_store import ProjectStore

# To support doctests only
import shutil

import orchid


# TODO: change `ifrac_pathname` to be `str` or `pathlib.Path`
@deal.pre(lambda ifrac_pathname: len(ifrac_pathname.strip()) != 0)
@deal.pre(lambda ifrac_pathname: ifrac_pathname is not None)
def load_project(ifrac_pathname: str) -> Project:
    """
    Return the project for the specified `.ifrac` file.

    Args:
        ifrac_pathname: The path identifying the data file of the project of interest.

    Returns:
        The project of interest.

    Examples:
        >>> load_path = orchid.training_data_path().joinpath('frankNstein_Bakken_UTM13_FEET.ifrac')
        >>> loaded_project = orchid.load_project(str(load_path))
        >>> loaded_project.name
        'frankNstein_Bakken_UTM13_FEET'
    """
    loader = ProjectStore(ifrac_pathname.strip())
    result = Project(loader)
    return result


# TODO: change `ifrac_pathname` to be `str` or `pathlib.Path`
@deal.pre(lambda project, _: project is not None)
@deal.pre(lambda _, ifrac_pathname: ifrac_pathname is not None)
@deal.pre(lambda _, ifrac_pathname: len(ifrac_pathname) != 0)
@deal.pre(lambda _, ifrac_pathname: len(ifrac_pathname.strip()) != 0)
def save_project(project: Project, ifrac_pathname: str) -> None:
    """
    Return the project for the specified `.ifrac` file.

    Args:
        ifrac_pathname: The path identifying the data file of the project of interest.
        project: The project of interest.

    Examples:
        >>> # Test saving changed project
        >>> load_path = orchid.training_data_path().joinpath('frankNstein_Bakken_UTM13_FEET.ifrac')
        >>> loaded_project = orchid.load_project(str(load_path))
        >>> save_path = load_path.with_name(f'salvus{load_path.suffix}')
        >>> orchid.save_project(loaded_project, str(save_path))
        >>> save_path.exists()
        True
        >>> save_path.unlink()
    """

    store = ProjectStore(ifrac_pathname.strip())
    store.save_project(project)


# TODO: change `ifrac_pathname` to be `str` or `pathlib.Path`
@deal.pre(lambda _: _.project is not None)
@deal.pre(lambda _: _.project is not None)
@deal.pre(lambda _: _.source_pathname is not None)
@deal.pre(lambda _: len(_.source_pathname) != 0)
@deal.pre(lambda _: len(_.source_pathname.strip()) != 0)
@deal.pre(lambda _: (_.maybe_target_pathname is None or
                     (_.maybe_target_pathname is not None and len(_.maybe_target_pathname) != 0)))
@deal.pre(lambda _: (_.maybe_target_pathname is None or
                     (_.maybe_target_pathname is not None and len(_.maybe_target_pathname.strip()) != 0)))
def optimized_but_possibly_unsafe_save(project: Project, source_pathname: str,
                                       maybe_target_pathname: Optional[str] = None):
    """
    Saves `project`, optionally to `maybe_to_pathname` is an optimized, but possibly "unsafe" manner.

    If `maybe_to_pathname` is supplied and is not `None`, it must be a string representing a valid pathname. If a file
    with that pathname already exists, it will be overwritten (unless it is the same path as `source_pathname`)

    This method is unsafe because it only writes some data from `project`; the remainder of the data is simply
    (bulk) copied from the `.ifrac` file, `source_pathname`.

    This method assumes that `project` was originally loaded from `project_pathname` and was then changed in
    such a way that the "bulk" data **was not** changed. If this assumption is not true, the project saved in
    `to_pathname` will **not** contain all the changes to `project`.

    Specifically, this method **does not** save changes to data like:

    - Trajectories
    - Treatment curves
    - Monitor curves

    We believe that this method will generally finish more quickly than `save_project`; however, we cannot
    guarantee this behavior. We encourage the developer calling this method to perform her own performance tests
    and to understand if his use case meets the assumptions made by this method.

    Args:
        project: The project to be saved.
        source_pathname: The pathname of the `.ifrac` file from which `project` was loaded.
        maybe_target_pathname: The optional pathname of the `.ifrac` file in which to store `project`.

    Examples:
        >>> # Test optimized but possibly unsafe save of project
        >>> load_path = orchid.training_data_path().joinpath('Project_frankNstein_Permian_UTM13_FEET.ifrac')
        >>> loaded_project = orchid.load_project(str(load_path))
        >>> save_path = load_path.with_name(f'salva intuta{load_path.suffix}')
        >>> orchid.optimized_but_possibly_unsafe_save(loaded_project, str(load_path), str(save_path))
        >>> save_path.exists()
        True
        >>> save_path.unlink()
        >>> # Test optimized but possibly unsafe save of project in loaded location
        >>> source_path = orchid.training_data_path().joinpath('Project_frankNstein_Permian_UTM13_FEET.ifrac')
        >>> load_path = source_path.with_name(f'idem salvum filum{source_path.suffix}')
        >>> # ignore returned result for doctest
        >>> _to_path = shutil.copyfile(str(source_path), str(load_path))
        >>> loaded_project = orchid.load_project(str(load_path))
        >>> orchid.optimized_but_possibly_unsafe_save(loaded_project, str(load_path))
        >>> load_path.exists()
        True
        >>> load_path.unlink()

    """
    store = ProjectStore(source_pathname.strip())
    store.optimized_but_possibly_unsafe_save(project, option.maybe(maybe_target_pathname))
