## Orchid Python API Release Notes

### A Reading Suggestion

This document is one of several documents you may want to read:

- [README](./README.md) - The project README file.
- [README-dev.md](./README-dev.md) - A similar file targeting for package developers.
- [ReleaseNotes.md](./ReleaseNotes.md) - The release notes for this project.

Although one can read this document in any text editor since it is simply a text file, consider installing
the [Python grip utility](https://pypi.org/project/grip/). This application allows one to "render local readme
files before sending off to GitHub". Although you need not send any of these file to `GitHub`, by using `grip` 
to render the file, you can much more easily navigate the document links.

### Release notes for 2022.2.324

This release is the production release of the Orchid Python API corresponding to Orchid 2022.2. This release:

- Implements a high-level (Pythonic) API to create stages and add them to a well
- Improves performance when loading an Orchid project by using a new .NET feature to load projects in parallel
- Implements a high-level "fast save" API. This API provides an optimized way of saving Orchid projects when
  certain conditions are met.
- Restore minimum Python version to 3.8.3
- Repaired `pandas.DataFrame.append` "Future Warning" in examples
- Add low-level example demonstrating creating and adding multi-picking observations to an observation set

#### Possible breaking .NET API changes

- .NET API renames `StageCorrectionStatus` to `CorrectionStatus`
- Added comments describing a work-around for the integer-valued stage attribute limitation
- Change the implementation of the Python API for stages to handle optional .NET values for the stage properties,
  `Isip`, `PNet` and `Shmin`

#### Resolved Issues

- [GitHub issue 35](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/35)
- [GitHub issue 34](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/34)
- [GitHub issue 33](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/33)
- [GitHub issue 32](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/32)

#### Features

- Well and Stage
  - Implements a high-level (Pythonic) API to create stages and add them to a well
  - Adds an example illustrating use of this API
  - Renames the original low-level example to `add_stages_low.py` to better communicate intent

- Saving projects
  - Implements an optimized but possibly unsafe function to save Orchid projects. If certain conditions are met
    (described in the docstring for `orchid.core.optimized_but_possibly_unsafe_save()`), one can use this function to
    save Orchid projects. The developer must determine if the particular use case meets the conditions to safely save
    the project using the optimized but possibly unsafe function.
    
    If the use case does not meet the conditions, the function, `orchid.core.save_project()`, safely saves the
    complete project, but, most likely, takes additional time over the optimized but possibly unsafe save function.

- Examples (high-level)
  - Add tutorial script to create stages and add them to a well

- Examples (low-level)
  - Repaired low-level (Python.NET) script to create stages and add them to a well
  - Add a low-level script demonstrating adding multi-picking observations to an observation set.

- Distribution
  - Reduce minimum required Python version to 3.8.3.

#### Known Issues

- [GitHub issue 36](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/36)

### Release notes for 2022.1.360

This release is the production release of the Orchid Python API corresponding to Orchid 2022.1. This release:

- Provides high-level access to downhole proppant concentrations
- Adds a high-level API property to change the stage time range
- Add a high-level example script to illustrate using the high-level API to change the stage time range
- Expose stage QC results via the high-level API
- Replace low-level script to read and write stage QC results with script invoking the high-level API
  (`stage_qc_results.py`)
- Repaired the low-level example script to create stage attributes to reflect changes to the .NET API
  (`auto_pick_and_create_stage_attribute.py`)
- Clarify documentation of the `PythonApiLibs` directory in configuration documentation

#### Resolved Issues

- [GitHub issue 25](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/25)
- [GitHub issue 26](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/26)
- [GitHub issue 28](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/28)
- [GitHub issue 30](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/30)
- [GitHub issue 31](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/31)

#### Features

- Project
  - Expose `user_data` property containing stage QC results

- Stage
  - Change the stage start and stop times (time range)

- Treatment curves
  - Add enumeration `DOWNHOLE_PROPPANT_CONCENTRATION` to access this data from the API

- Project user data
  - Create class `NativeUserDataAdapter` to provide read and write access to this information

- Examples (high-level)
  - Add script to read and write stage QC results
  - Add script to change the stage start and stop times
  - 
- Examples (low-level)
  - Repaired script to create stage attributes
  - Removed script to query the stage QC results using the low-level API

- Distribution
  - None

#### Known Issues

- [GitHub issue 27](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/27)
- [GitHub issue 29](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/29)

### Release notes for 2021.4.283

This release is the production release of the Orchid Python API corresponding to Orchid 2021.4. This release:

- Adds several low-level examples
- Repairs stage center MDKB calculation
- Adds well trajectory methods
- Clarifies installed package requirements
- Work-around to clarify `PythonApiLibs` in configuration

#### Resolved Issues

- [GitHub issue 24](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/24)

#### Features

- Well trajectory
  - TVDSS
  - Inclination
  - Azimuth
  - MDKB

- Project
  - Clarifies direction of project azimuth

- Stage
  - Corrects stage center MDKB calculation

- Examples (low-level)
  - Adding observations and saving changed projects
  - Matching low-level monitor time series and high-level project time series (A low-level workaround for
    [GitHub issue 17](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/17)
  - Creating stage attributes
    
- Distribution
  - Adds generation of `requirements.txt` to release process

#### Known Issues

- [GitHub issue 25](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/25)

### Release notes for 2021.3.406

This release is a hot fix release of the Orchid Python API corresponding to the hot fix for Orchid 2021.3. 
This release:

- Improves the performance of the `plot_time_series` example
- Improves the performance of the `volume_2_first_response` example

#### Resolved Issues

- [GitHub issue 23](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/23)

#### Features

No additional features as part of this release.

#### Known Issues

No additional know issues for this release.

### Release notes for 2021.3.381

This release is the production release of the Orchid Python API corresponding to Orchid 2021.3. This release:

- Adds an iterator over "searchable project objects"
- Add a tutorial demonstrating how to navigate the project
- Prototype developer scripts to generate documentation using Sphinx

#### Resolved Issues

- [GitHub issue 22](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/22)

#### Features

- SearchableProjectObjects
  - Make class an iterator

- Tutorials
  - A notebook and script demonstrating project object navigation

#### Known Issues

No additional know issues for this release.

### Release notes for 2021.2.316

This release is the production release of the Orchid Python API corresponding to Orchid 2021.2. This release:

- Updates to the latest version of `numpy`
- Exposes data frames via the API
- Internally uses `pendulum` for improved handling of date times (both UTC and local times)
- Provides a consistent interface for collections of DOM objects

#### Resolved Issues

- [GitHub issue 12](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/12)
- [GitHub issue 16](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/16)
- [GitHub issue 18](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/18)
- [GitHub issue 21](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/21)

#### Features

- Project
  - Data frames
- Stage
  - Find stages by:
    - Display stage number
    - Display name with well

- Object collections
  - Find object(s) by
    - Display name
    - Name
    - Object ID
    - All objects satisfying a predicate (primarily a convenience for use cases where the condition of interest does 
      not involve identifying information). Note that stages have some of these convenience methods already.
  - Query collection for
    - All display names
    - All names
    - All object IDs
    - All objects (primarily a convenience for use cases where one wants all objects in the collection independent 
      of identifying information)

- Examples
  - Scripts for each example notebook
  - A notebook and script demonstrating search and data frame access.

#### Known Issues

- [GitHub issue 19](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/19)

### Release notes for 2021.1.399

This release is the second production release of the Orchid Python API. This release changes the 
implementation of measurements to use the [pint](https://pint.readthedocs.io/en/stable/) package and adds
access to additional Orchid features.

#### Resolved issues

- [GitHub issue 6](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/6)
- [GitHub issue 10](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/10)
- [GitHub issue 13](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/13)
- [GitHub issue 14](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/14)
- [GitHub issue 15](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/15)

#### Features

- Project
  - Azimuth
  - Fluid density
  - Project bounds
  - Project center (and center location)
  - Monitors
- Well
  - Formation
  - Wellhead location
- Monitor
  - Name
  - Display name
  - Start time
  - Stop time
  - Time range (contains start and stop time)
- Examples
  - Volume to first response
  
Replace custom `Measurement` class with the features available in `pint`.

#### Known issues

- [GitHub issue 18](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/18)
  
  This issue is a deprecation warning from `matplotlib`. It began occurring after updating the package
  dependencies. We do not believe this error will affect customer code.

- [GitHub issue 16](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/16)
  
  All monitor curves can be access indirectly via the `Project.monitor_curves()` method. The work-around for
  this issue is then to search for curves by with a matching name.
  
- [GitHub issue 17](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/17)

  The work-around is to search the iterable returned by Project.monitor_curves for a curve with the name of
  the monitor of interest. Because of issue #16, beware that this work around may not return all monitors
  with the name of interest.

### Release notes for 2020.4.690

This release is the first production release of the Orchid Python API. This release offers access to the
following Orchid features.

#### Features

- General
  - Loading Orchid `.ifrac` files
- Project
  - Name
  - Project units
  - Wells
  - Default well colors
  - Monitor curves
  - Searching for wells by name
- Well
  - Name
  - Display name
  - Stages
  - Trajectory
  - UWI
- Stage
  - Cluster count
  - Display name with well
  - Display name without well
  - Display stage number
  - Global stage sequence number
  - Order of completion on well
  - Stage (formation connection) type
  - Start time
  - Stop time
  - Bottom location
  - Center location
    - In addition, to the subsurface point
      - Easting
      - Northing
      - Measured depth (MD)
      - Total vertical depth (TVD) relative to
        - Ground level
        - Seal level
      - XY (both easting and northing)
  - Cluster location
  - Instantaneous shut in pressure (ISIP)
  - Measured depth of stage top
  - Measured depth of stage bottom
  - Net pressure (PNet)
  - Minimum shear (ShMin)
  - Stage length
  - Top location
  - Treatment curves
- TimeSeries (monitor and treatment curves)
  - Name
  - Display name
  - Sampled quantity name
  - Sampled quantity unit
  - Time series
- Calculations
  - For treatment
    - Median treating pressure
    - Pumped fluid volume
    - Total proppant mass

#### Known issues

- [GitHub issue 18](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/18)
  
  This issue is a deprecation warning from `matplotlib`. It began occurring after updating the package
  dependencies. We do not believe this error will affect customer code.
  
- [GitHub issue 14](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/14)

  The work-around for this issue is to configure the locations of both Orchid training data and the Orchid
  binaries.

- [GitHub issue 13](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/13)

  We believe that this warning is caused by the `pandas` package interacting with `numpy`, and plan to
  investigate this issue.

- [GitHub issue 12](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/12)
  
  Some versions of `numpy` encounter an issue with the `fmod` function on Windows. The current work-around
  fixes the version of `numpy` at 1.19.3.
  
- [GitHub issue 10](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/10)

  Although we have increased the scope of our internal testing to cover many more units of measure, we plan to
  implement the convenience function suggested by the author.
  
- [GitHub issue 6](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/6)

  This issue is an internal issues and currently has no effect on installation or usage of the API.

- [GitHub issue 3](https://github.com/Reveal-Energy-Services/orchid-python-api/issues/3)

  This issue may relate to `numpy` 1.19.1 (the version mentioned in the issue). We plan to retest against 
  `numpy` 1.19.3. We have had no other reports of this issue.
