# CZModel provides simple-to-use conversion tools to generate a CZANN to be used in ZEISS ZEN Intellesis Portfolio
# Copyright 2022 Carl Zeiss Microscopy GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# To obtain a commercial version please contact Carl Zeiss Microscopy GmbH.
"""Utility functions for input checking in argument parser."""
import argparse
import os


def dir_file(path: str) -> str:
    """Helper type for arg parser to check if passed argument is a valid file.

    Args:
        path: path to check

    Returns:
        path if valid

    Raises:
        ArgumentTypeError: path determined not to be a valid file
    """
    if os.path.isfile(path):
        return path

    raise argparse.ArgumentTypeError("Given argument is not a valid file")


def dir_path(path: str) -> str:
    """Helper type for arg parser to check if passed argument is a valid directory.

    Args:
        path: path to check

    Returns:
        path if valid

    Raises:
        ArgumentTypeError: path determined not to be a valid directory
    """
    if os.path.isdir(path):
        return path

    raise argparse.ArgumentTypeError("Given argument is not a valid directory")
