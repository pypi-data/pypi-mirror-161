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

import pathlib
import pprint
from uuid import UUID

import pandas as pd

import orchid

# Load the Orchid project
default_file_name_to_read = pathlib.Path('frankNstein_Bakken_UTM13_FEET.ifrac')
default_project_path_name_to_read = str(orchid.training_data_path().joinpath(default_file_name_to_read))
project = orchid.load_project(default_project_path_name_to_read)

# Get a dictionary mapping object IDs to project time series
time_series = {ts.object_id: ts for ts in project.time_series().all_objects()}
print('\nAll time series in project')
pprint.pprint(time_series)

# Get a .NET (native) monitor whose time series you want to use
monitors = {m.object_id: m for m in project.monitors().all_objects()}
print('\nAll monitors in project')
pprint.pprint(monitors)

# In this particular scenario, I'm simply going to pick the first monitor from a dictionary mapping object IDs
# to native_monitor_adapters.
monitor_oid = UUID('5b68d8c4-a578-44e7-bc08-b1d83483c4ec')
monitor = monitors[monitor_oid]
print('\nMonitor of interest:')
print(f'  - Object ID: {monitor.object_id}')
print(f'  - Display Name: {monitor.display_name}')

# Extract the object ID of the time series associated with this monitor
monitor_time_series_native_oid = monitors[monitor_oid].dom_object.TimeSeries.ObjectId
monitor_time_series_oid = UUID(str(monitor_time_series_native_oid))
print(f'\nObject ID of monitor time series of interest: {monitor_time_series_oid}')

# And get the time series identified by this object ID
time_series_for_monitor = project.time_series().find_by_object_id(monitor_time_series_oid)

# Finally, get the time series as a `pandas` (time) `Series`
time_series_of_interest = time_series_for_monitor.data_points()
print('\nHead of time series')
print(time_series_of_interest.head())

