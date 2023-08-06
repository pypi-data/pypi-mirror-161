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
"""Common logic for utility functions."""
from typing import List
from czmodel.model_metadata import ModelMetadata


def validate_metadata(metadata: ModelMetadata, model_input_shape: List[int], model_output_shape: List[int]) -> None:
    """Validates the correctness of the model metadata given information about the actual model.

    Arguments:
        metadata: The model metadata object containing all the czann meta data.
        model_input_shape: The actual input shape of the model (without a batch dimension).
        model_output_shape: The actual output shape of the model (without a batch dimension).

    Raises:
        ValueError: If the provided meta data is not consistent in itself or with the actual model.
    """
    if len(model_input_shape) != len(metadata.input_shape) or not all(
        model_dim in (None, 0, meta_dim) for meta_dim, model_dim in zip(metadata.input_shape, model_input_shape)
    ):
        raise ValueError(
            f"The input shape of the provided model ({list(model_input_shape)}) is not consistent "
            f"with the input shape provided in the metadata ({metadata.input_shape})"
        )
    if len(model_output_shape) != len(metadata.output_shape) or not all(
        model_dim in (None, 0, meta_dim) for meta_dim, model_dim in zip(metadata.output_shape, model_output_shape)
    ):
        raise ValueError(
            f"The output shape of the provided model ({list(model_output_shape)}) is not consistent "
            f"with the output shape provided in the metadata ({metadata.output_shape})"
        )
    if metadata.min_overlap is not None and len(metadata.min_overlap) == len(metadata.input_shape):
        raise ValueError(
            f"If a minimum overlap is specified it must provide values for all spatial dimensions."
            f"Spatial dimensions of the model are: {metadata.input_shape[:-1]}. "
            f"Define overlaps are: {metadata.min_overlap}."
        )


def validate_legacy_metadata(  # type: ignore  # Ignored argument
    _, model_input_shape: List[int], model_output_shape: List[int]
) -> None:
    """Validates the correctness of the model metadata given information about the actual model.

    Arguments:
        model_input_shape: The actual input shape of the model (without a batch dimension).
        model_output_shape: The actual output shape of the model (without a batch dimension).

    Raises:
        ValueError: If the provided meta data is not consistent in itself or with the actual model.
    """
    if model_input_shape[0] in (None, 0) or model_input_shape[1] in (None, 0):
        raise ValueError(
            f"The input shape of the provided model ({list(model_input_shape)}) must define all spatial dimensions."
        )
    if model_output_shape[0] in (None, 0) or model_output_shape[1] in (None, 0):
        raise ValueError(
            f"The output shape of the provided model ({list(model_output_shape)}) must define all spatial dimensions."
        )
