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
"""This module provides data structures to represent the meta-data of a CZANN containing a TensorFlow Keras model."""
import json
import uuid
from enum import Enum
from typing import Dict, List, Any, NamedTuple, Union, Optional, TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from tensorflow.keras import Model


class ModelType(Enum):
    """Enum representing the different model types supported by czann."""

    SINGLE_CLASS_INSTANCE_SEGMENTATION = "SingleClassInstanceSegmentation"
    MULTI_CLASS_INSTANCE_SEGMENTATION = "MultiClassInstanceSegmentation"
    SINGLE_CLASS_SEMANTIC_SEGMENTATION = "SingleClassSemanticSegmentation"
    MULTI_CLASS_SEMANTIC_SEGMENTATION = "MultiClassSemanticSegmentation"
    SINGLE_CLASS_CLASSIFICATION = "SingleClassClassification"
    MULTI_CLASS_CLASSIFICATION = "MultiClassClassification"
    OBJECT_DETECTION = "ObjectDetection"
    REGRESSION = "Regression"


class _ModelMetadata(NamedTuple):
    """Base class representing the metadata of a model.

    Attributes:
        model_type: The type of model.
        input_shape: The input shape expected by the model.
        output_shape: The shape of the output produced by the model.
        model_id: The id of the model. Must be a UUID. If no id is provided,
            a new random id will be generated automatically.
        model_name: The name of the generated model.
        classes: A list of class names corresponding to the output dimensions of the predicted segmentation mask.
            If the last dimension of the prediction has shape n the provided list must be of length n.
        min_overlap: The minimum needed overlap of tiles in a tiled inference setup that is added to
            an input image such that there are no border effects visible in the required area of the generated
            output. For deep architectures this value can be infeasibly large so that the border size
            must be defined in a way that the border effects are “acceptable” in the ANN model creator’s opinion.
        scaling: The extents of a pixel in x- and y-direction (in that order) in units of m.
    """

    model_type: ModelType
    input_shape: List[int]
    output_shape: List[int]
    model_id: str
    min_overlap: Optional[List[int]] = None
    classes: Optional[List[str]] = None
    model_name: Optional[str] = None
    scaling: Optional[Tuple[float, float]] = None

    @staticmethod
    def from_json(model_metadata: Union[str, Dict]) -> "ModelMetadata":
        """This function parses a model specification JSON file to a ModelMetadata object.

        Args:
            model_metadata: The path to the JSON file containing the
                model specification or the specification object itself.

        Returns:
            A ModelMetadata instance carrying all information to generate a CZANN file.
        """
        meta_data: Dict
        # Load spec from json if necessary
        if isinstance(model_metadata, str):
            with open(model_metadata, "r", encoding="utf-8") as f:
                meta_data = json.load(f)
        else:
            meta_data = model_metadata

        return ModelMetadata(
            model_type=ModelType(meta_data["Type"]),
            input_shape=meta_data["InputShape"],
            output_shape=meta_data["OutputShape"],
            model_id=str(meta_data["Id"]) if "Id" in meta_data else None,
            model_name=meta_data.get("ModelName"),
            classes=meta_data.get("Classes"),
            min_overlap=meta_data.get("MinOverlap"),
            scaling=tuple(meta_data["Scaling"]) if "Scaling" in meta_data else None,
        )

    def to_czann_dict(self) -> Dict:
        """Creates an XML representation of the model meta data.

        Returns:
            A dictionary representing the czann meta information.
        """

        def add_if_not_none(target: Dict, key: str, value: Any) -> Dict:
            if value is not None:
                target[key] = value
            return target

        # Create result dict
        result: Dict[str, Any] = {
            "Id": self.model_id,
            "Type": self.model_type.value,
            "InputShape": self.input_shape,
            "OutputShape": self.output_shape,
        }
        result = add_if_not_none(result, "MinOverlap", self.min_overlap)
        result = add_if_not_none(result, "Classes", self.classes)
        result = add_if_not_none(result, "ModelName", self.model_name)
        result = add_if_not_none(result, "Scaling", self.scaling)

        return result


class ModelMetadata(_ModelMetadata):
    """Class representing the metadata of a model automatically initializing the model id if not passed explicitly.

    Attributes:
        model_type: The type of model.
        input_shape: The input shape expected by the model.
        output_shape: The shape of the output produced by the model.
        model_id: The id of the model. Must be a UUID. If no id is provided,
            a new random id will be generated automatically.
        model_name: The name of the generated model.
        classes: A list of class names corresponding to the output dimensions of the predicted segmentation mask.
            If the last dimension of the prediction has shape n the provided list must be of length n.
        min_overlap: The minimum needed overlap of of tiles in a tiled inference setup that is added to
            an input image such that there are no border effects visible in the required area of the generated
            output. For deep architectures this value can be infeasibly large so that the border size
            must be defined in a way that the border effects are “acceptable” in the ANN model creator’s opinion.
        scaling: The extents of a pixel in x- and y-direction (in that order) in units of m.
    """

    __slots__ = ()

    def __new__(cls, *args: Any, model_id: Optional[str] = None, **kwargs: Any) -> "ModelMetadata":
        """Creates a new instance of the class initializing the model id properly.

        Arguments:
            args: Properties to initialize the metadata object.
            model_id: A UUID representing the model id or None.
            kwargs: Keyword properties to initialize the meta data object.
        """
        return super().__new__(  # type: ignore  # False positive
            cls, *args, model_id=str(uuid.uuid4()) if model_id is None else model_id, **kwargs
        )


class ModelSpec(NamedTuple):
    """Model specification tuple.

    Attributes:
        model: Either the path to a TensorFlow Keras model on disk or the model object itself.
        model_metadata: The metadata of the model.
        license_file: The path to a license file that is added to the generated CZANN. Can be absolute or
            relative to the JSON file.
    """

    model: Union[str, "Model"]
    model_metadata: ModelMetadata
    license_file: Optional[str] = None

    @staticmethod
    def from_json(model_spec_path: str) -> "ModelSpec":
        """This function parses a model specification JSON file to a ModelSpec object.

        Args:
            model_spec_path: The path to the JSON file containing the model specification.

        Returns:
            A ModelMetadata instance carrying all information to generate a CZANN file.
        """
        with open(model_spec_path, "r", encoding="utf-8") as f:
            spec = json.load(f)

        return ModelSpec(
            model=spec["ModelPath"],
            license_file=spec.get("LicenseFile"),
            model_metadata=ModelMetadata.from_json(spec["ModelMetadata"]),
        )
