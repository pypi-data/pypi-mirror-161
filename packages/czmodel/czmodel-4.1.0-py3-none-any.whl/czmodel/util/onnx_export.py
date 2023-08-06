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
"""Provides conversion utility functions for ONNX models."""
from io import BytesIO
from typing import Optional, Callable, List, Union, Generic, TypeVar
import onnx

from czmodel.util.model_packing import create_model_zip, create_legacy_model_zip
from czmodel.util.common import (
    validate_metadata as common_validate_metadata,
    validate_legacy_metadata as common_validate_legacy_metadata,
)
from czmodel.model_metadata import ModelMetadata
from czmodel.legacy_model_metadata import ModelMetadata as LegacyModelMetadata


T = TypeVar("T", ModelMetadata, LegacyModelMetadata)


class BaseOnnxConverter(Generic[T]):
    """Base class for converting ONNX models to an export format of the czmodel library."""

    def __init__(
        self,
        conversion_fn: Callable[[Union[str, bytes, memoryview], T, str, Optional[str]], None],
        validate_metadata_fn: Callable[[T, List[int], List[int]], None],
    ):
        """Initializes the converter and stores the conversion and meta data validation function.

        Arguments:
            conversion_fn: The function to convert a given model, meta data, output path and license file
                to the desired export format.
            validate_metadata_fn: Function that validates a given model meta data, model input shape
                and model output shape. This function raises a ValueError if the the provided values
                do not comply with the specification.
        """
        super().__init__()
        self._conversion_fn: Callable[[Union[str, bytes, memoryview], T, str, Optional[str]], None] = conversion_fn
        self._validate_metadata: Callable[[T, List[int], List[int]], None] = validate_metadata_fn

    def convert(
        self,
        model: str,
        model_metadata: T,
        output_path: str,
        license_file: Optional[str] = None,
    ) -> None:
        """Wraps a given ONNX model into a czann container.

        Args:
            model: ONNX model to be converted.
            model_metadata: The metadata required to generate a model in export format.
            output_path: Destination path to the model file that will be generated.
            license_file: Path to a license file.

        Raises:
            ValueError: If the input or output shapes of the model and the meta data do not match.
        """
        # Check if model input and output shape is consistent with provided metadata
        onnx_model = onnx.shape_inference.infer_shapes(onnx.load(model))
        input_shape = [dim.dim_value for dim in onnx_model.graph.input[0].type.tensor_type.shape.dim][1:]
        output_shape = [dim.dim_value for dim in onnx_model.graph.output[0].type.tensor_type.shape.dim][1:]
        self._validate_metadata(
            model_metadata,
            input_shape,
            output_shape,
        )

        # Pack model into czann
        with open(model, "rb") as f:
            buffer = BytesIO(f.read())
            self._conversion_fn(buffer.getbuffer(), model_metadata, output_path, license_file)


class DefaultOnnxConverter(BaseOnnxConverter[ModelMetadata]):
    """Base class for converting ONNX models to the czann format."""

    def __init__(self) -> None:
        """Initializes the converter."""
        super().__init__(
            conversion_fn=create_model_zip,
            validate_metadata_fn=common_validate_metadata,
        )


class LegacyOnnxConverter(BaseOnnxConverter[LegacyModelMetadata]):
    """Base class for converting ONNX models to the czmodel format."""

    def __init__(self) -> None:
        """Initializes the converter."""
        super().__init__(
            conversion_fn=create_legacy_model_zip,
            validate_metadata_fn=common_validate_legacy_metadata,
        )
