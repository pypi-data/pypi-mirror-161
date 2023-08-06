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
"""Provides extraction functions to unpack a .czann/.czseg file."""
import os
import zipfile
from pathlib import Path
from typing import Tuple
from czmodel.model_metadata import ModelMetadata
from czmodel.legacy_model_metadata import ModelMetadata as LegacyModelMetadata


def _extract(zip_filename: str, target_dir: os.PathLike) -> None:
    """Extract a ZIP file to a target directory

    Args:
        zip_filename: Path of ZIP file
        target_dir: Target directory
    """
    # extract the model file into a temporary directory
    with zipfile.ZipFile(zip_filename) as z:
        z.extractall(str(target_dir))


def extract_czann_model(path: str, target_dir: Path) -> Tuple["ModelMetadata", os.PathLike]:
    """Extract the metadata from a .czann model

    Args:
        path: Path of the .czann file
        target_dir: Target directory for the extraction

    Returns:
        Tuple containing the model metadata and the model itself in that order
    """
    # extract the model file
    _extract(path, target_dir)

    # get the metadata file
    metadata_file = _find_metadata_file(target_dir, ".json")

    # get the model file
    model_file = _find_model_file(target_dir)

    # get the information of the model as a dictionary
    model_dict = ModelMetadata.from_json(str(metadata_file))
    return model_dict, model_file


def extract_czseg_model(path: str, target_dir: Path) -> Tuple["LegacyModelMetadata", os.PathLike]:
    """Extract the metadata from a .czseg/.czmodel model

    Args:
        path: Path of the .czseg/.czmodel file
        target_dir: Target directory for the extraction

    Returns:
        Tuple containing the model metadata and the model itself in that order
    """
    # extract the model file
    _extract(path, target_dir)

    # get the metadata file
    metadata_file = _find_metadata_file(target_dir, ".xml")

    # get the model file
    model_file = _find_model_file(target_dir)

    # get the information of the model as a dictionary
    model_dict = LegacyModelMetadata.from_xml(str(metadata_file))
    return model_dict, model_file


def _find_model_file(target_dir: Path) -> os.PathLike:
    """Find the model file itself

    Args:
        target_dir: Directory to search

    Raises:
        RuntimeError: No model file is found in the path

    Returns:
        Path of the model file
    """
    model_file = next((target_dir.glob("*.model")), None)
    if not model_file:
        raise RuntimeError("No model file is found!")
    return model_file


def _find_metadata_file(target_dir: Path, extension: str) -> os.PathLike:
    """Find the metadata file of a model

    Args:
        target_dir: Directory to search
        extension: Extension (including a leading .) of the metadata file.

    Raises:
        RuntimeError: No metadata file is found in the path

    Returns:
        Path of the model file
    """
    files = target_dir.glob("*")
    metadata_file = next((target_dir / file for file in files if file.suffix == extension), None)
    if not metadata_file:
        raise RuntimeError("No metadata file is found!")
    return metadata_file
