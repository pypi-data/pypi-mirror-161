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
"""Provides transformations to be added as pre- or post-processing layers to a model utilities."""
from typing import Optional, Sequence, Tuple, Union, Any
import collections.abc
import warnings
import numpy as np

import tensorflow as tf


class TransposeChannels(tf.keras.layers.Layer):
    """A Keras layer that rearranges the channel order of inputs."""

    def __init__(self, order: Tuple[int, ...], *args: Any, **kwargs: Any) -> None:
        """Initializes the layer.

        Arguments:
            order: The order in which the channel dimension will be shuffled.
            *args: Additional arguments that will be passed to the TensorFlow Layer constructor.
            **kwargs: Additional keyword arguments that will be passed to the TensorFlow Layer constructor.

        Raises:
            ValueError: If the provided order contains negative values or does not define an order without gaps.
        """
        super().__init__(*args, **kwargs)
        if any(elem < 0 for elem in order):
            raise ValueError("All values in the order tuple must be non-negative.")
        if sorted(order) != list(range(len(order))):
            gaps = set(range(max(order))).difference(set(order))
            raise ValueError(
                f"The order tuple must fully define order without gaps. "
                f"The order tuple contains the following gaps: {sorted(list(gaps))}."
            )
        self.order = order

    @tf.function
    def call(  # pylint: disable=W0613 # kwargs required by TensorFlow
        self, inputs: tf.Tensor, **kwargs: Any
    ) -> tf.Tensor:
        """Rearranges the channel order of the inputs.

        Args:
            inputs: An input tensor with the channels in the last dimension.
            **kwargs: Additional keyword arguments.

        Returns:
            The inputs with rearranged channel order.

        Raises:
            ValueError: If the number of channels in the input tensor does not
                comply with the defined order.
        """
        if inputs.shape[-1] <= max(self.order):
            raise ValueError(
                f"The received input tensor has {inputs.shape[-1]} channels "
                f"but the order tuple defines {max(self.order)} channels."
            )
        return tf.stack([inputs[..., order] for order in self.order], axis=-1)


class PerImageStandardization(tf.keras.layers.Layer):
    """A Keras pre-processing layer that applies per image standardization."""

    @tf.function
    def call(  # pylint: disable=W0613 # kwargs required by TensorFlow
        self, inputs: tf.Tensor, **kwargs: Any
    ) -> tf.Tensor:
        """Shifts and linearly scales each image.

         The image will have mean 0 and variance 1. The image is implicitly converted to float representation.

        Args:
            inputs: The image(s) to be standardized.
            **kwargs: Additional keyword arguments.

        Returns:
            The standardized image.
        """
        if inputs.dtype != tf.float32:
            inputs = tf.image.convert_image_dtype(inputs, dtype=tf.float32)

        return tf.image.per_image_standardization(inputs)


class Shift(tf.keras.layers.Layer):
    """A Keras layer that shifts the data."""

    def __init__(self, shift: Tuple[float, ...], *args: Any, **kwargs: Any) -> None:
        """Creates an instance of the shift layer.

        Args:
            shift: The shift to be applied to the entire dataset.
            args: Additional arguments to be passed to the base Layer class.
            kwargs: Additional keyword arguments to be passed to the base Layer class.
        """
        super().__init__(*args, **kwargs)
        self._shift = tf.convert_to_tensor(shift)
        if not np.isfinite(np.asarray(shift)).all():
            warnings.warn("The defined shift contains infinite values. This may lead to numerical issues.")

    @tf.function
    def call(  # pylint: disable=W0613 # kwargs required by TensorFlow
        self, inputs: tf.Tensor, **kwargs: Any
    ) -> tf.Tensor:
        """Shifts and image by constant values.

        Args:
            inputs: The image(s) to be shifted.
            **kwargs: Additional keyword arguments.

        Returns:
            The shifted image.
        """
        return inputs + tf.cast(self._shift, inputs.dtype)


class Scale(tf.keras.layers.Layer):
    """A Keras layer that scales the data."""

    def __init__(self, scale: Tuple[float, ...], *args: Any, **kwargs: Any) -> None:
        """Creates an instance of the scale layer.

        Args:
            scale: The scale to be applied to the entire dataset.
            args: Additional arguments to be passed to the base Layer class.
            kwargs: Additional keyword arguments to be passed to the base Layer class.
        """
        super().__init__(*args, **kwargs)
        self._scale = tf.convert_to_tensor(scale)
        if not np.isfinite(np.asarray(scale)).all():
            warnings.warn("The defined scale contains infinite values. This may lead to numerical issues.")

    @tf.function
    def call(  # pylint: disable=W0613 # kwargs required by TensorFlow
        self, inputs: tf.Tensor, **kwargs: Any
    ) -> tf.Tensor:
        """Scales an image by constant values.

        Args:
            inputs: The image(s) to be scaled.
            **kwargs: Additional keyword arguments.

        Returns:
            The scaled image.
        """
        return inputs * tf.cast(self._scale, inputs.dtype)


class SigmoidToSoftmaxScores(tf.keras.layers.Layer):
    """A Keras layer for converting sigmoidal output to softmax scores."""

    @tf.function
    def call(  # pylint: disable=W0613 # kwargs required by TensorFlow
        self, inputs: tf.Tensor, **kwargs: Any
    ) -> tf.Tensor:
        """Performs the conversion from sigmoidal outputs to softmax scores in the last dimension.

        Args:
            inputs: An output from a layer with sigmoid activation. The last dimension must be of size 1.
            **kwargs: Additional keyword arguments.

        Returns:
            The probability distribution as generated by a softmax layer.

        Raises:
            ValueError: If the last dimension of the input does not have exactly size 1.
        """
        if inputs.shape[-1] != 1:
            raise ValueError(
                f"The shape of the sigmoid activated input must be 1 on the last dimension. "
                f"Received Tensor of shape {inputs.shape}"
            )
        return tf.concat([inputs, tf.constant(1.0) - inputs], -1)


def add_preprocessing_layers(
    model: tf.keras.Model,
    layers: Optional[Union[tf.keras.layers.Layer, Sequence[tf.keras.layers.Layer]]] = None,
    spatial_dims: Optional[Tuple[int, int]] = None,
) -> tf.keras.Model:
    """Prepends a given pre-processing layer to a given Keras model.

    Args:
        model: The Keras model to be wrapped.
        layers: The layers to be prepended.
        spatial_dims: Set new spatial dimensions for the input node. This parameter is expected to contain the
            new height and width in that order. Note: Setting this parameter is only possible for models
            that are invariant to the spatial dimensions of the input such as FCNs.

    Returns:
        A new Keras model wrapping the provided Keras model and the pre-processing layers.
    """
    # Handle single layer and None input
    if layers is None:
        layers = []
    elif not isinstance(layers, collections.abc.Sequence):
        layers = [layers]

    # Create input layer
    new_shape = (
        (model.inputs[0].shape[0],) + spatial_dims + (model.inputs[0].shape[-1],)
        if spatial_dims is not None
        else model.inputs[0].shape
    )
    input_layer = tf.keras.Input(batch_shape=new_shape, name="input")

    # Apply pre-processing layer
    converted = input_layer
    for layer in layers:
        converted = layer(converted)

    # Apply model
    outputs = model(converted)

    # Return new Keras model
    return tf.keras.Model(inputs=input_layer, outputs=outputs)


def add_postprocessing_layers(
    model: tf.keras.Model,
    layers: Optional[Union[tf.keras.layers.Layer, Sequence[tf.keras.layers.Layer]]],
) -> tf.keras.Model:
    """Appends a given post-processing layer to a given Keras model.

    Args:
        model: The Keras model to be wrapped.
        layers: The layers to be appended.

    Returns:
        A new Keras model wrapping the provided Keras model and the post-processing layers.
    """
    # Handle single layer and None input
    if layers is None:
        layers = []
    elif not isinstance(layers, collections.abc.Sequence):
        layers = [layers]

    # Apply model
    inputs = model.inputs
    outputs = model(inputs)

    for layer in layers:
        outputs = layer(outputs)

    # Return new Keras model
    return tf.keras.Model(inputs=inputs, outputs=outputs)
