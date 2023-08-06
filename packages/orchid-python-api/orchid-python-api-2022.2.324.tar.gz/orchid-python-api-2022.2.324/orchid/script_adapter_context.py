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


import sys

import orchid.configuration

import toolz.curried as toolz

# noinspection PyPackageRequirements
import clr
# noinspection PyUnresolvedReferences
from System import InvalidOperationException


def append_orchid_assemblies_directory_path() -> None:
    """
    Append the directory containing the required Orchid assemblies to `sys.path`.
    """
    orchid_bin_dir = toolz.get_in(['orchid', 'root'], orchid.configuration.python_api())
    if orchid_bin_dir not in sys.path:
        sys.path.append(orchid_bin_dir)


append_orchid_assemblies_directory_path()

clr.AddReference('Orchid.FractureDiagnostics.SDKFacade')
# noinspection PyUnresolvedReferences
from Orchid.FractureDiagnostics.SDKFacade import ScriptAdapter


class ScriptAdapterContext:
    """
    A "private" class with the responsibility to initialize and shutdown the .NET ScriptAdapter class.

    I considered making `ProjectStore` a context manager; however, the API then becomes somewhat unclear.

        - Does the constructor enter the context? Must a caller initialize the instance and then enter the
          context?
        - What results if a caller *does not* enter the context?
        - Enters the context twice?

    Because I was uncertain I created this private class to model the `ScriptAdapter` context. The property,
    `ProjectStore.native_project`, enters the context if it will actually read the project and exits the
    context when the read operation is finished.

    For information on Python context managers, see
    [the Python docs](https://docs.python.org/3.8/library/stdtypes.html#context-manager-types)
    """

    def __enter__(self):
        try:
            ScriptAdapter.Init()
            return self
        # TODO: Correct exception type / DEADFALL issue
        except InvalidOperationException as ioe:
            if 'REVEAL-CORE-0xDEADFA11' in ioe.Message:
                print('Orchid licensing error. Please contact Orchid technical support.')
                sys.exit(-1)
            else:
                raise

    def __exit__(self, exc_type, exc_val, exc_tb):
        ScriptAdapter.Shutdown()
        # Returning no value will propagate the exception to the caller in the normal way
        return
