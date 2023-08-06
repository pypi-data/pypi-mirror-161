## Introduction 

This project defines the implementation of the Python API for Orchid*.

Specifically, the `orchid` package makes Orchid features available to Python applications and to the
Python REPL.

(* Orchid is a mark of Reveal Energy Services, Inc.)

### A Reading Suggestion

This document is one of several documents you may want to read:

- [README](./README.md) - This file.
- [README-dev.md](./README-dev.md) - A similar file targeting for package developers.
- [ReleaseNotes.md](./ReleaseNotes.md) - The release notes for this project.

Although one can read this document in any text editor since it is simply a text file, consider installing
the [Python grip utility](https://pypi.org/project/grip/). This application allows one to "render local readme
files before sending off to GitHub". Although you need not send any of these file to `GitHub`, by using `grip` 
to render the file, you can much more easily navigate the document links.

## Examples

### High-level examples

This project includes eight scripts and six notebooks in the `examples` directory of the `orchid-python-api` package:

| Name                            | Demonstrates...                                                                     |
|---------------------------------|-------------------------------------------------------------------------------------|
| `completion_analysis.ipynb`     | A detailed analysis of the completion performed on two different wells in a project |
| `plot_trajectories.ipynb`       | Plotting the well trajectories for a project                                        |
| `plot_time_series.ipynb`        | Plotting the monitor curves for a project                                           |
| `plot_treatment.ipynb`          | Plotting the treatment curves for a specific stage of a well in a project           | 
| `search_data_frames.ipynb`      | Searching object collections and our data frame access                              | 
| `volume_2_first_response.ipynb` | Using derivatives to calculate the fluid volume pumped before the first response    | 

Six of the eight scripts contain the same code as the notebooks but run either at the command line or in a REPL. The
last three scripts:

| Name                            | Demonstrates using the high-level Python API to...                               |
|---------------------------------|----------------------------------------------------------------------------------|
| `stage_qc_results.py`           | Read and write QC results for a stage. (Replaces low-level `stage_qc_status.py`) |
| `change_stage_times.py`         | Change the start and stop times (the time range) of a stage                      |
| `add_stages.py`                 | Add one or more stages to a well. (Improvement over `add_stages_low.py`)         |

### Low-level examples

In addition, this project includes five scripts and a notebook in the `examples/low_level` directory of the
`orchid-python-api` package:

| Name                                      | Demonstrates...                                                  |
|-------------------------------------------|------------------------------------------------------------------|
| `auto_pick.py`                            | Automatically pick observations and save them to an .ifrac file  |
| `auto_pick_and_create_stage_attribute.py` | Create and save stage attributes                                 |
| `auto_pick_iterate_example.py`            | Use iteration to find visible stages instead of .NET method      |
| `monitor_time_series.py`                  | Find high-level time series from a low-level monitor time series | 
| `add_stages_low.py`                       | Adds newly created stages to a well of a project                 | 
| `multi_picking_events.py`                 | Creates and adds a number of multi-picking events                |

The notebook, `auto_pick.ipynb` contain the same code as the script, `auto_pick.py`, but runs in a Jupyter
notebook.
 
To use these examples: 

- You may need to 
  [configure the Orchid Python API to find the Orchid installation](#configure-the-orchid-python-api)
- You **must** 
  [configure the Orchid Python API to find the Orchid training data](#configure-the-orchid-training-data)
- You may need to [view the Orchid API configuration details](#view-orchid-configuration-details)
- You may want to invoke the command, `copy_orchid_examples`

    This command copies the example files into an optionally specified (virtual environment) directory. (The 
    default destination is your current working directory.) Note that this command is a command-line script 
    that runs in a console or terminal. Additionally, this command supports a help flag, `-h` or `--help`, to 
    provide you with help on running this command.

More detailed instructions for running the examples can be found at:

- [Run Orchid high-level examples](#run-orchid-high-level-examples).

## Tutorials

Additionally, this project includes one notebook and one script in the `tutorials` directory of the
`orchid-python-api` package:

- `dom_navigation_tutorial.ipynb`
- `dom_navigation_tutorial.py`

The notebook, `dom_navigation_tutorial.ipynb`, demonstrates using the Orchid Python API class,
`SearchableProjectObjects`, to navigate a project. The `SearchableProjectObjects` provides:

- Three query methods:
    - `all_names()`
    - `all_display_names()`
    - `all_object_ids()`
- Three specific search methods:
    - `find_by_name()`
    - `find_by_display_name()`
    - `find_by_object_id()`
- A general search method:
    - `find()` - This method expects a predicate to identify project objects of interest
- Two general iteration methods:
  - `all_objects()`
  - `SearchableProjectObjects` is an _iterator_

The script contains code similar to the notebook but runs either at the command line or in a REPL.

To use these tutorials:

- You may need to
  [configure the Orchid Python API to find the Orchid installation](#configure-the-orchid-python-api)
- You **must**
  [configure the Orchid Python API to find the Orchid training data](#configure-the-orchid-training-data)
- You may need to [view the Orchid API configuration details](#view-orchid-configuration-details)
- You may want to invoke the command, `copy_orchid_tutorials`

  This command copies the tutorial files into an optionally specified (virtual environment) directory. (The
  default destination is your current working directory.) Note that this command is a command-line script
  that runs in a console or terminal. Additionally, this command supports a help flag, `-h` or `--help`, to
  provide you with help on running this command.

More detailed instructions for running the tutorials can be found at:

- [Run Orchid tutorials](#run-orchid-tutorials).

## Getting Started

### Virtual environments

We recommend the use of virtual environments to use the Orchid Python API. This choice avoids putting 
Orchid-specific packages in your system Python environment.

You have several options to create and manage virtual environments: `venv`, `pipenv`, `poetry`, and `conda`.
The `venv ` is available as a standard Python package and is a spartan tool to manage environments. `poetry`
is a tool targeting developers but can be used by end-users. Our recommended tool is `pipenv`. It provides a 
good balance between `venv ` and `poetry`. Remember, both `pipenv` and `poetry` must be installed in your 
Python environment separately from Python itself, but can be installed using `pip`. Finally, 
[conda](https://docs.conda.io/en/latest/)

> is an open source package management system and environment management system that runs on Windows, macOS
> and Linux. Conda quickly installs, runs and updates packages and their dependencies. Conda easily creates,
> saves, loads and switches between environments on your local computer. It was created for Python programs,
> but it can package and distribute software for any language.

We recommend the use of `pipenv`. This environment hides a number of details involved in managing a virtual
environment and yet provides a fairly simple interface. We will assume in this document that you are using
`pipenv`.

Although we recommend `pipenv`, because we understand many of our users use `conda` (either Anaconda or
Miniconda), we have a [section](#step-by-step-conda-install) for installing the `orchid-python-api` in a
`conda` virtual environment.

Using any of `pipenv`, `venv` or `poetry`, your first step is to create a directory for **your** project.
Then, change into that project directory.

### Step-by-step pipenv install

- Install python 3.8 by following [these installation instructions](https://docs.python.org/3/using/windows.html). To 
  ensure access from the command line, be sure to select the "Add Python 3.x to PATH" option on the
  [installer start page](https://docs.python.org/3/_images/win_installer.png). 
- Open a console using either `powershell` or the Windows console.
- Create a directory for the virtual environment. We will symbolically call it `/path/to/orchid-virtualenv`.
- Change the current working directory by executing, `chdir /path/to/orchid-virtualenv`.
- Create an empty virtual environment by running `pipenv install`.
- Activate the virtual environment by running `pipenv shell`
- Install Orchid by running `pip install orchid-python-api`.

### Step-by-step conda install

- Install [Anaconda](https://docs.anaconda.com/anaconda/install/) or
  [Miniconda](https://docs.conda.io/en/latest/miniconda.html) following the corresponding instructions for
  your operating system. 
- If installing on Windows, the installer will present 
  [this screen](https://docs.anaconda.com/_images/win-install-options.png). We have seen no need to install 
  Anaconda / Miniconda on your [PATH](https://en.wikipedia.org/wiki/PATH_(variable)). Although we do not
  disagree with option to register the Anaconda / Miniconda version of Python as your default Python
  executable, in some situations, accepting this choice can cause problems. 
- Since we will be using **both** `conda install` and `pip install` to install packages, read the article, 
  [Using Pip in a Conda Environment](https://www.anaconda.com/blog/using-pip-in-a-conda-environment). Our 
  subsequent instructions assume you have read this article and have chosen how you wish to manage these
  two package installers together. 
  
The following instructions assume that you will use the simple (put perhaps not scalable) process of creating
the `conda` virtual environment with all packages you want to use available in the Anaconda/Miniconda
ecosystem and, within that virtual environment, use `pip` to install `orchid-python-api`.

- Open an Anaconda Powershell console.
- Optionally create a directory for your work.
    - We symbolically call it `/path/to/orchid-virtualenv`.
    - Change to the current working directory by executing `chdir /path/to/orchid-virtualenv`.
- Create an empty virtual environment by running `conda create --name <your-virtualenv-name> python=3.8`.
- Activate the virtual environment by running `conda activate <your-virtualenv_name>`
- Install Orchid by running `pip install orchid-python-api`.

### Using a requirements file

An alternative method used by customers uses a requirements file, `requirements.txt`, that we create as part of our
release process but **do not** include in our distribution. 
[This file](https://github.com/Reveal-Energy-Services/orchid-python-api/blob/master/requirements.txt) is available
from our GitHub repository. For `pipenv`, use 
[these import instructions](https://pipenv-fork.readthedocs.io/en/latest/basics.html#importing-from-requirements-txt). For
`conda`, read the accepted answer to this 
[Stack Overflow post](https://stackoverflow.com/questions/63379968/using-requirements-txt-to-automatically-install-packages-from-conda-channels-and)
for the correct command and additional options you may need to consider.

### Configure the Orchid Python API

The Orchid Python API requires a licensed Orchid installation on your workstation. Depending on the details of
the installation, you may need to configure the Orchid Python API to refer to different locations.

#### Using the fallback configuration

If you installed the latest version Orchid using the installation defaults, and you installed the
`orchid-python-api` using the [pipenv installation instructions](#step-by-step-pipenv-install) or 
the [conda installation instructions](#step-by-step-conda-install), you need to take **no** additional
steps to configure the Orchid Python API to find this installation. For your information, the default
installation location is, `%ProgramFiles%\Reveal Energy Services\Orchid`. The Orchid Python API uses the API
version to find and use the corresponding version of Orchid.

#### Using an environment variable

This mechanism is perhaps the easiest procedure to create an Orchid Python API configuration that changes 
rarely and is available to all your tools. It works best with a system restart. (Environment variables can be 
made available for a narrow set of tools on your system or available to all your tools depending on arcane
technical rules that you need not understand.) 

To use environment variables to configure the Orchid Python API, you will need to create the environment
variable `ORCHID_ROOT` and set its value to the path of the `PythonApiLibs` directory beneath the Orchid
installation directory. (For your information, the `PythonApiLibs` directory containing the version-specific
Orchid binary and configuration files should be in a subdirectory like 
`ORCHID_ROOT/Orchid-2020.4.232/PythonApiLibs` when you accept the installation defaults.) 

This section assumes you want to create a long-term configuration that survives a system restart and is
available to all your tools. Symbolically, this document will refer to the directory containing the binaries
required by the Orchid Python API as `/path-to/orchid/version/python-api-libs`.

To create the required environment variable, enter the search term "environment variables" in the Windows-10 
search box and select the item named, "Edit environment variables for your account." The system will then 
present you with the "Environment Variables" dialog. Under the section named "User variables for 
<your.username>", click the "New" button. In the "Variable name" text box, enter "ORCHID_ROOT". (These two 
words are separated by the underscore symbol.)

Navigate to the "Variable Value" text box. Click the "Browse Directory" button to select the directory into
which Orchid is installed, `/path-to/orchid/version/python-api-libs`. This action pastes the directory
name into the "Variable Value" text box. Verify that the directory is correct, and then click "OK". Verify
that you see the name `ORCHID_ROOT` with the correct value in the "User variables for <your.username>" list.
Finally, click "OK" to dismiss the "Environment Variables" dialog.

Although you have created the `ORCHID_ROOT` environment variable with the appropriate value, only "new" opened
tools can use that variable. However, the details of "new" is technical and may not correspond to what you
expect. If you understand these details, you can jump to 
[Verify Installation](#verify-installation). If you are not confident of these details, restart
your system before proceeding to [Verify Installation](#verify-installation).

#### Using a configuration file

Another option to configure the Orchid Python API is by creating a configuration file. A configuration file is
easier to change than an environment variable and does not require a system restart to work best. However, it
requires more knowledge and work on your part. In general, a configuration file is better if your requirements
change "often". For example, if you are working with multiple, side-by-side Orchid versions and Orchid Python 
API versions, you may find it faster and easier to create a configuration file once and change it as you 
change Orchid / Orchid Python API versions.

To use a file to configure the Orchid Python API, you will need to create a configuration file named
`python_api.yaml` and set the value of the `orchid` > `root` key to the path of the `PythonApiLibs` directory
beneath the Orchid installation directory. (For your information, the `PythonApiLibs` directory containing the
version-specific Orchid binary and configuration files should be in a subdirectory like
`ORCHID_ROOT/Orchid-2020.4.232/PythonApiLibs` when you accept the installation defaults.)

Symbolically, this document will refer to the directory containing the binaries required by the
Orchid Python API as `/path-to/orchid/version/python-api-libs`.

To create a configuration file used by the Orchid Python API, you must:

- Create the directory, `/path/to/home-directory/.orchid`, where `/path/to/home-directory` is a symbolic
  reference to your home directory.
- Create the file, `python_api.yaml` in `/path/to/home-directory/.orchid`.

Technically, the format of the file is `YAML` ("YAML Ain't Markup Language"), a "human friendly data
serialization standard". (For technical details, visit [the website](https://yaml.org/). For a gentler
introduction, visit [the Wikipedia entry](https://en.wikipedia.org/wiki/YAML) or read / watch one of the many
`YAML` introductions / tutorials.)

Because these articles describe `YAML` generally, they **do not** describe the details of the `YAML` document
expected by the Orchid Python API. We, however, distribute an example file name `python_api.yaml.example` in
each installed `orchid-python-api` package. Assuming you created a virtual environment as described in
the step-by-step [pipenv installation instructions](#step-by-step-pipenv-install) or
the [conda installation instructions](#step-by-step-conda-install) section, you can find this example file,
`python_api.yaml.example`, in the directory,
`/path/to/orchid-virtualenv/Lib/site-packages/orchid_python_api/examples`. 

To use this configuration file as an example:

- Copy the file to the expected location. For example, assuming the symbolic names referenced above, execute:
  ```
  copy /path/to/orchid-virtualenv/Lib/site-packages/orchid_python_api/examples/python_api.yaml.example /path/to/home-directory/.orchid/python_api.yaml
  ```
- Edit the copied file, `/path/to/home-directory/.orchid/python_api.yaml`, using your favorite **text** editor.

The example file, contains comments, introduced by a leading octothorpe character (#, number sign, or hash),
that describe the information expected by the Orchid Python API. In summary, you'll need to provide a value
for the `orchid` > `root` key that contains (symbolically), `/path-to/orchid/version/python-api-libs`.

If you want to ensure your configuration is correct,
[view the Orchid API configuration details](#view-orchid-configuration-details).

### Configure the Orchid training data

Using the Orchid Python API **requires** a licensed Orchid installation on your workstation. However,
to use the example Jupyter notebooks or scripts, you **must** configure the Orchid Python API to find the
Orchid training data.

#### Using an environment variable

This mechanism is perhaps the easiest procedure to create an Orchid Python API configuration that changes 
rarely and is available to all your tools. It works best with a system restart. (Environment variables can be 
made available for a narrow set of tools on your system or available to all your tools depending on arcane
technical rules that you need not understand.) 

To use environment variables to configure the Orchid Python API to find the Orchid training data, you will 
need to create the environment variable `ORCHID_TRAINING_DATA` and set its value to the location of the Orchid 
training data.

This document assumes you want to create a long-term configuration that survives a system restart and is 
available to all your tools. Symbolically, this document will refer to the Orchid training data location as
`/path-to/orchid/training-data`. 

To create the required environment variable, enter the search term "environment variables" in the Windows-10 
search box and select the item named, "Edit environment variables for your account." The system will then 
present your with the "Environment Variables" dialog. Under the section named "User variables for 
<your.username>", click the "New" button. In the "Variable name" text box, enter "ORCHID_TRAINING_DATA".
(These three words are separated by the underscore symbol.)

Navigate to the "Variable Value" text box. Click the "Browse Directory" button to select the directory 
containing the Orchid training data, `/path-to/orchid/training-data`. This action pastes the directory name
into the "Variable Value" text box. Verify that the directory is correct, and then click "OK". Verify that
you see the name `ORCHID_TRAINING_DATA` with the correct value in the "User variables for <your.username>"
list. Finally, click "OK" to dismiss the "Environment Variables" dialog.

Although you have now created the `ORCHID_TRAINING_DATA` environment variable with the appropriate value,
only "new" tools can now use that variable. However, the details of "new" is technical and may not correspond
to your what you expect. If you understand these details, you can jump to
[Verify Installation](#verify-installation). If you are not confident of these details, restart
your system before proceeding to [Verify Installation](#verify-installation).

#### Using a configuration file

Another option to configure the Orchid Python API to find the Orchid training data is by creating a 
configuration file. A configuration file is easier to change than an environment variable and does not require 
a system restart to work best. However, it requires more knowledge and work on your part. In general, a 
configuration file is better if your requirements change "often". For example, if you are working with 
multiple, side-by-side Orchid versions and Orchid Python API versions, you may find it faster and easier to
create a configuration file once and change it as you change Orchid / Orchid Python API versions or training
data locations.

To create a configuration file used by the Orchid Python API, you create a file named `python_api.yaml`
and put it in the directory, `/path/to/home-directory/.orchid`, where `/path/to/home-directory` is a 
symbolic reference to your home directory. Technically, the format of the file is `YAML` ("YAML Ain't Markup
Language"), a "human friendly data serialization standard". (For technical details, visit
[the website](https://yaml.org/). For a gentler introduction, visit 
[the Wikipedia entry](https://en.wikipedia.org/wiki/YAML) or read / watch on of the many `YAML` 
introductions / tutorials.)

Because these articles describe `YAML` generally, they **do not** describe the details of the `YAML` document
expected by the Orchid Python API. We, however, distribute an example file name `python_api.yaml.example` in
each installed `orchid-python-api` package. Assuming you created a virtual environment as described in
the step-by-step [pipenv installation instructions](#step-by-step-pipenv-install) or the 
[conda installation instructions](#step-by-step-conda-install), you can find this example file,
`python_api.yaml.example`, in the directory,
`/path/to/orchid-virtualenv/Lib/site-packages/orchid_python_api/examples`.

To use this configuration file as an example:

- Copy the file to the expected location. For example, assuming the symbolic names referenced above, execute
  the command
  
  ```
  copy /path/to/orchid-virtualenv/Lib/site-packages/orchid_python_api/examples/python_api.yaml.example /path/to/home-directory/.orchid/python_api.yaml
  ```  
  
- Edit the copied file, `/path/to/home-directory/.orchid/python_api.yaml`, using your favorite **text** editor.

The example file, contains comments, introduced by a leading octothorpe character (#, number sign, or hash),
that describe the information expected by the Orchid Python API. In summary, you'll need to provide a value
for the 'orchid' > 'training_data' key that contains the pathname of the directory containing the Orchid
training data files.

If you want to ensure your configuration is correct,
[view the Orchid API configuration details](#view-orchid-configuration-details).

## Verify installation

### Jupyter lab

- In your activated virtual environment, run `jupyter lab` to open a browser tab.
- In the first cell, enter `import orchid`.
- Run the cell.
- Wait patiently.

The import should complete with no errors.

### Python REPL

- In your activated virtual environment, run either `python` or `ipython` to open a REPL.
- Enter `import orchid`.
- Wait patiently.

The import should complete with no errors.

## Run Orchid high-level examples

- If you have not already done so, 
[configure the Orchid Python API to find the Orchid installation](#configure-the-orchid-python-api)
- You **must** 
[configure the Orchid Python API to find the Orchid training data](#configure-the-orchid-training-data)
- Navigate to the directory associated with the virtual environment
- If necessary, activate the virtual environment by executing either 
    - `pipenv shell` or 
    - `conda activate <your-virtualenv_name>`.
- Run `copy_orchid_examples`
- If the script reports that it skipped notebooks or scripts, repeat the command with an additional argument:  
  `copy_orchid_examples --overwrite`
- Verify that the current directory has six example notebooks:
    - `completion_analysis.ipynb`
    - `plot_time_series.ipynb`
    - `plot_trajectories.ipynb`
    - `plot_treatment.ipynb`
    - `search_data_frames.ipynb`
    - `volume_2_first_response.ipynb`
- Verify that the current directory has nine example scripts:
    - `completion_analysis.py`
    - `plot_time_series.py`
    - `plot_trajectories.py`
    - `plot_treatment.py`
    - `search_data_frames.py`
    - `volume_2_first_response.py`
    - `stage_qc_results.py`
    - `change_stage_times.py`
    - `add_stages.py`

### Run high-level example scripts

- Run the first script
    - Execute the command `python plot_trajectories.py`
    - Wait patiently for the `matplotlib` plot window to appear.
    - Ensure the plot is correct.
    - Dismiss the `matplotlib` window.
- Repeat for these scripts:
    - `plot_treatment.py`
    - `plot_time_series.py` 
    - `completion_analysis.py` (This script prints multiple messages and presents **multiple** plots.
       You must dismiss each plot to continue.)
    - `volume_2_first_response.py`
    - `search_data_frames.py`
- Run the `stage_qc_results.py` script.
- Run the `change_stage_times.py` script.
- Run the `add_stages.py` script.

The scripts, `stage_qc_results.py`, `change_stage_times.py`, and `add_stages.py`, differ from the other scripts. These
scripts require a number of command line arguments to run correctly.

For example, to see an explanation of these arguments, execute any of this scripts with the `--help` option.
The most typical arguments are described in the following paragraphs.

To both read and write stage QC results, run the command:
```
python stage_qc_results.py -v2 /path/to/orchid-traing-data/frankNstein_Bakken_UTM13_FEET.v11.ifrac 
```

To only read the existing stage QC data, run the command
```
python stage_qc_results.py -v2 --read-only /path/to/orchid-traing-data/frankNstein_Bakken_UTM13_FEET.v11.ifrac
```

To change the stage start and stop times (the time range), run the command
```
python change_stage_times.py -v2 /path/to/orchid-traing-data/frankNstein_Bakken_UTM13_FEET.v11.ifrac 
```

To add stages to a well, run the command
```
python add_stages.py -v2 /path/to/orchid-traing-data/frankNstein_Bakken_UTM13_FEET.v11.ifrac 
```

### Run high-level example notebooks

- Open Jupyter by running `jupyter lab` in the shell
- Within Jupyter,
    - Successfully run notebook, `plot_trajectories.ipynb`
        1. Open notebook
        2. Run all cells of notebook
        3. Wait patiently
        4. Verify that no exceptions occurred
    - Repeat for remaining notebooks:
        - `plot_time_series.ipynb`
        - `plot_treatment.ipynb`
        - `completion_analysis.ipynb`
        - `volume_2_first_response.ipynb`
        - `search_data_frames.ipynb`

## Run Orchid tutorials

- If you have not already done so,
  [configure the Orchid Python API to find the Orchid installation](#configure-the-orchid-python-api)
- You **must**
  [configure the Orchid Python API to find the Orchid training data](#configure-the-orchid-training-data)
- Navigate to the directory associated with the virtual environment
- If necessary, activate the virtual environment by executing either
    - `pipenv shell` or
    - `conda activate <your-virtualenv_name>`.
- Run `copy_orchid_tutorials.exe`
- If the script reports that it skipped notebooks or scripts, repeat the command with an additional argument:  
  `python </path/to/virtualenv/Lib/site-packages/copy_orchid_tutorials.py --overwrite`
- Verify that the current directory has one tutorial notebooks:
    - `dom_navigation_tutorial.ipynb`
- Verify that the current directory has five example scripts:
    - `dom_navigation_tutorial.py`

### Run tutorial script

- Run the `dom_navigation_tutorial.py` script
    - Execute the command `python dom_navigation_tutorial.py`
    - Follow the on-screen messages to advance through the tutorial

### Run tutorial notebook

- Open Jupyter by running `jupyter lab` in the shell
- Within Jupyter,
    - Run the notebook, `dom_navigation_tutorial.ipynb`
        1. Open the notebook in `jupyter`
        2. Run each cell of the notebook. Typically, this process involves
            - Read the instructions or comments preceding the code cell(s)
            - Observe the result of executing the code

## View Orchid Configuration Details

To "debug" the Orchid Python API configuration, perform the following steps:

- Change to the directory associated with your Python virtual environment.
- If necessary, activate the virtual environment.
- Within that virtual environment, invoke Python. It is important to create a new REPL so that you start with
  a "clean" environment.
- Within the Python REPL, execute the following commands.

  ```
  import logging
  logging.basicConfig(level=logging.DEBUG)
  import orchid
  ```
  
Enabling logging **before** importing is critical. If you have already imported `orchid`, the simplest
solution is to close this REPL and create another, "clean" REPL.

You should see output like the following:

```
DEBUG:orchid.configuration:fallback configuration={'orchid': {'root': 'C:\\Program Files\\Reveal Energy Services\\Orchid\\Orchid-2020.4.361'}}
DEBUG:orchid.configuration:file configuration={'orchid': {'root': 'c:\\path-to\\bin\\x64\\Debug\\net48', 'training_data ': 'c:\\path-to\\installed-training-data'}}
DEBUG:orchid.configuration:environment configuration = {'orchid': {'root': 'c:\\another\\path-to\bin\\x64\\Debug\\net48'}}
DEBUG:orchid.configuration:result configuration={'orchid': {'root': 'c:\\another\\path-to\bin\\x64\\Debug\\net48'}}
```

This output describes four details of the configuration.

| Configuration | Explanation                                                            |
|---------------|------------------------------------------------------------------------|
| fallback      | The always available configuration (may be empty)                      |
| file          | The configuration specified in your configuration file (may be empty)  |
| environment   | The configuration specified using environment variables (may be empty) | 
| result        | The configuration used by the Orchid Python API (should not be empty)  |

