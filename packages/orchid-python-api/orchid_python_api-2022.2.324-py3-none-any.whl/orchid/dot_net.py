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


import os
import pathlib

import orchid.configuration
import orchid.script_adapter_context as sac

import toolz.curried as toolz

# noinspection PyPackageRequirements
import clr


def add_orchid_assemblies() -> None:
    """
    Add references to the Orchid assemblies needed by the Python API.

    Although not all modules in the `orchid` package need .NET types from all the available Orchid assemblies,
    I believe the additional cost of adding those references is far less than the cost of maintaining the
    copy-paste, boilerplate code that results without this common function.
    :return:
    """
    clr.AddReference('Orchid.Common')
    clr.AddReference('Orchid.FractureDiagnostics')
    clr.AddReference('Orchid.FractureDiagnostics.Factories')
    clr.AddReference('UnitsNet')
    clr.AddReference('System.Collections')
    return None


def app_settings_path() -> str:
    """
    Return the pathname of the `appSettings.json` file needed by the `SDKFacade` assembly.

    :return: The required pathname.
    """
    result = os.fspath(pathlib.Path(toolz.get_in(['orchid', 'root'],
                                                 orchid.configuration.python_api())).joinpath('appSettings.json'))
    return result


def prepare_imports() -> None:
    # This function call must occur *after*
    # - Importing clr
    # - Adding a reference to `Orchid.FractureDiagnostics.SDKFacade`
    # - Importing ScriptAdapter from `Orchid.FractureDiagnostics.SDKFacade`
    # - The call to `append_orchid_assemblies_directory_path`
    with sac.ScriptAdapterContext():
        orchid.dot_net.add_orchid_assemblies()
