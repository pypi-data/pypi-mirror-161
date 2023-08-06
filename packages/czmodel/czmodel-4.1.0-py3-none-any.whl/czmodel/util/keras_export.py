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
"""Provides conversion utility functions for Keras models."""
import logging
import os
import tempfile
from io import BytesIO
from typing import (
    Sequence,
    Tuple,
    List,
    Union,
    Optional,
    Dict,
    TYPE_CHECKING,
    Callable,
    Generic,
    TypeVar,
)
from zipfile import ZipFile

import onnx
import tensorflow as tf
from tf2onnx import tf_loader, utils, optimizer
from tf2onnx.tfonnx import process_tf_graph

from czmodel.util.model_packing import (
    create_model_zip,
    create_legacy_model_zip,
    zip_directory,
)
from czmodel.util.transforms import add_preprocessing_layers, add_postprocessing_layers
from czmodel.util.common import (
    validate_metadata as common_validate_metadata,
    validate_legacy_metadata as common_validate_legacy_metadata,
)
from czmodel.model_metadata import ModelMetadata
from czmodel.legacy_model_metadata import ModelMetadata as LegacyModelMetadata

if TYPE_CHECKING:
    from tensorflow.keras import Model
    from tensorflow.keras.layers import Layer


T = TypeVar("T", ModelMetadata, LegacyModelMetadata)


_ONNX_OPSET = 12


def convert_saved_model_to_onnx(
    saved_model_dir: str,
    output_file: str,
    target: Optional[Sequence] = None,
    custom_op_handlers: Optional[Dict] = None,
    extra_opset: Optional[Sequence] = None,
) -> None:
    """Exports a SavedModel on disk to an ONNX file.

    Arguments:
        saved_model_dir: The directory containing the model in SavedModel format.
        output_file: The path to the file to be created for the ONNX model.
        target: Workarounds applied to help certain platforms.
        custom_op_handlers: Handlers for custom operations.
        extra_opset: Extra opset, for example the opset used by custom ops.
    """
    graph_def, inputs, outputs = tf_loader.from_saved_model(saved_model_dir, None, None)

    with tf.Graph().as_default() as tf_graph:
        tf.import_graph_def(graph_def, name="")

    with tf_loader.tf_session(graph=tf_graph):
        g = process_tf_graph(
            tf_graph,
            continue_on_error=False,
            target=target,
            opset=_ONNX_OPSET,
            custom_op_handlers=custom_op_handlers,
            extra_opset=extra_opset,
            input_names=inputs,
            output_names=outputs,
        )

    onnx_graph = optimizer.optimize_graph(g)

    model_proto = onnx_graph.make_model(f"Model {os.path.split(saved_model_dir)[1]} in ONNX format")

    utils.save_protobuf(output_file, model_proto)

    # Verify model's structure and check for valid model schema
    onnx.checker.check_model(output_file)


class BaseKerasConverter(Generic[T]):
    """Base class for converting Keras models to an export format of the czmodel library."""

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
        model: "Model",
        model_metadata: T,
        output_path: str,
        license_file: Optional[str] = None,
        spatial_dims: Optional[Tuple[int, int]] = None,
        preprocessing: Union["Layer", Sequence["Layer"]] = None,
        postprocessing: Union["Layer", Sequence["Layer"]] = None,
    ) -> None:
        """Converts a given Keras model to either an ONNX model or (upon failure) to a TensorFlow saved_model.

        The exported model is optimized for inference.

        Args:
            model: Keras model to be converted. The model must have a separate InputLayer as input node.
            model_metadata: The metadata required to generate a model in export format.
            output_path: Destination path to the model file that will be generated.
            license_file: The path to a license file to be included in the model.
            spatial_dims: New spatial dimensions for the input node (see final usage for more details)
            preprocessing: The layers to be prepended.
            postprocessing: The layers to be appended.

        Raises:
            ValueError: If the input or output shapes of the model and the meta data do not match.
        """
        if preprocessing is not None or spatial_dims is not None:
            model = add_preprocessing_layers(model=model, layers=preprocessing, spatial_dims=spatial_dims)

        if postprocessing is not None:
            model = add_postprocessing_layers(model=model, layers=postprocessing)

        # Check if model input and output shape is consistent with provided metadata
        input_shape = model.input_shape[1:]
        output_shape = model.output_shape[1:]
        self._validate_metadata(model_metadata, input_shape, output_shape)

        with tempfile.TemporaryDirectory() as tmpdir_saved_model_name:
            with tempfile.TemporaryDirectory() as tmpdir_onnx_name:
                # Export Keras model in SavedModel format
                model.save(tmpdir_saved_model_name, include_optimizer=False, save_format="tf")
                try:
                    # Convert to ONNX
                    onnx_path = os.path.join(tmpdir_onnx_name, "model.onnx")
                    convert_saved_model_to_onnx(tmpdir_saved_model_name, onnx_path)
                    with open(onnx_path, "rb") as f:
                        buffer = BytesIO(f.read())
                except Exception:
                    # Log fallback to SavedModel
                    logging.warning(
                        "Model could not be converted to ONNX format. "
                        "Falling back to SavedModel format. "
                        "Using this format is discouraged."
                    )
                    # Zip saved model
                    buffer = BytesIO()
                    with ZipFile(buffer, mode="w") as zf:
                        zip_directory(tmpdir_saved_model_name, zf)

                # Pack model into export format
                self._conversion_fn(buffer.getbuffer(), model_metadata, output_path, license_file)


class DefaultKerasConverter(BaseKerasConverter[ModelMetadata]):
    """Converts ONNX models to the czann format."""

    def __init__(self) -> None:
        """Initializes the converter."""
        super().__init__(
            conversion_fn=create_model_zip,
            validate_metadata_fn=common_validate_metadata,
        )


class LegacyKerasConverter(BaseKerasConverter[LegacyModelMetadata]):
    """Converts Keras models to the czmodel format."""

    def __init__(self) -> None:
        """Initializes the converter."""
        super().__init__(
            conversion_fn=create_legacy_model_zip,
            validate_metadata_fn=common_validate_legacy_metadata,
        )
