#! /usr/bin/env python
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


import argparse
import glob
import pathlib
import shutil
import site
import sys
from typing import Optional, Sequence


def site_packages_path() -> pathlib.Path:
    candidate_site_packages = [pn for pn in site.getsitepackages() if pn.find('site-packages') != -1]
    assert len(candidate_site_packages) == 1

    result = pathlib.Path(candidate_site_packages[0])
    return result


def copy_tutorials_to(target_dir: str, overwrite: bool) -> None:
    """
    Copy the Orchid Python API tutorials into the specified, `target_dir`.
    Args:
        target_dir: The target for the examples.
        overwrite: Flag: true if script will overwrite existing files with the same name in the target_dir.
    """

    def tutorial_candidates(filename_glob):
        tutorial_glob = str(site_packages_path().joinpath('orchid_python_api', 'tutorials', filename_glob))
        return glob.glob(tutorial_glob), tutorial_glob

    tutorial_notebook_candidates, tutorial_notebook_glob = tutorial_candidates('*.ipynb')
    if not tutorial_notebook_candidates:
        print(f'No tutorial notebooks matching "{tutorial_notebook_glob}"')
        return

    tutorial_script_candidates, tutorial_script_glob = tutorial_candidates('*.py')
    if not tutorial_script_candidates:
        print(f'No tutorial scripts matching "{tutorial_script_glob}"')
        return

    candidates = tutorial_notebook_candidates + tutorial_script_candidates
    for src in candidates:
        target_path = pathlib.Path(target_dir).joinpath(pathlib.Path(src).name)
        duplicate_in_target = target_path.exists()
        if duplicate_in_target and not overwrite:
            print(f'Skipping "{src}". Already exists.')
        else:
            shutil.copy2(src, target_dir)
            print(f'Copied "{src}" to "{target_dir}"')


def main(cli_args: Optional[Sequence[str]] = None):
    """
    Entry point for copy Orchid tutorials utility.
    Args:
        cli_args: The command line arguments.
    """
    cli_args = cli_args if cli_args else sys.argv[1:]

    parser = argparse.ArgumentParser(
        description='Copy Orchid Python API tutorial from installed package to specified directory')
    parser.add_argument('-t', '--target-dir', default='.',
                        help='Directory into which to copy the Orchid Python API tutorials '
                             '(default: current directory)')
    parser.add_argument('-o', '--overwrite', action='store_true', default=False,
                        help='Overwrite existing files in target directory',)

    args = parser.parse_args(cli_args)
    copy_tutorials_to(args.target_dir, args.overwrite)


if __name__ == '__main__':
    main(sys.argv[1:])
