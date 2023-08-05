# Copyright 2019 The FastEstimator Authors. All Rights Reserved.
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
# ==============================================================================
from typing import Dict, Optional, TypeVar

import tensorflow as tf
import torch

from fastestimator.backend._reduce_mean import reduce_mean

Tensor = TypeVar('Tensor', tf.Tensor, torch.Tensor)
Weight_Dict = TypeVar('Weight_Dict', tf.lookup.StaticHashTable, Dict[int, float])


def categorical_crossentropy(y_pred: Tensor,
                             y_true: Tensor,
                             from_logits: bool = False,
                             average_loss: bool = True,
                             class_weights: Optional[Weight_Dict] = None) -> Tensor:
    """Compute categorical crossentropy.

    Note that if any of the `y_pred` values are exactly 0, this will result in a NaN output. If `from_logits` is
    False, then each entry of `y_pred` should sum to 1. If they don't sum to 1 then tf and torch backends will
    result in different numerical values.

    This method can be used with TensorFlow tensors:
    ```python
    true = tf.constant([[0, 1, 0], [1, 0, 0], [0, 0, 1]])
    pred = tf.constant([[0.1, 0.8, 0.1], [0.9, 0.05, 0.05], [0.1, 0.2, 0.7]])
    weights = tf.lookup.StaticHashTable(
        tf.lookup.KeyValueTensorInitializer(tf.constant([1, 2]), tf.constant([2.0, 3.0])), default_value=1.0)
    b = fe.backend.categorical_crossentropy(y_pred=pred, y_true=true)  # 0.228
    b = fe.backend.categorical_crossentropy(y_pred=pred, y_true=true, average_loss=False)  # [0.223, 0.105, 0.356]
    b = fe.backend.categorical_crossentropy(y_pred=pred, y_true=true, average_loss=False, class_weights=weights)
    # [0.446, 0.105, 1.068]
    ```

    This method can be used with PyTorch tensors:
    ```python
    true = torch.tensor([[0, 1, 0], [1, 0, 0], [0, 0, 1]])
    pred = torch.tensor([[0.1, 0.8, 0.1], [0.9, 0.05, 0.05], [0.1, 0.2, 0.7]])
    weights = {1: 2.0, 2: 3.0}
    b = fe.backend.categorical_crossentropy(y_pred=pred, y_true=true)  # 0.228
    b = fe.backend.categorical_crossentropy(y_pred=pred, y_true=true, average_loss=False)  # [0.223, 0.105, 0.356]
    b = fe.backend.categorical_crossentropy(y_pred=pred, y_true=true, average_loss=False, class_weights=weights)
    # [0.446, 0.105, 1.068]
    ```

    Args:
        y_pred: Prediction with a shape like (Batch, C). dtype: float32 or float16.
        y_true: Ground truth class labels with a shape like `y_pred`. dtype: int or float32 or float16.
        from_logits: Whether y_pred is from logits. If True, a softmax will be applied to the prediction.
        average_loss: Whether to average the element-wise loss.
        class_weights: Mapping of class indices to a weight for weighting the loss function. Useful when you need to pay
            more attention to samples from an under-represented class.

    Returns:
        The categorical crossentropy between `y_pred` and `y_true`. A scalar if `average_loss` is True, else a
        tensor with the shape (Batch).

    Raises:
        AssertionError: If `y_true` or `y_pred` are unacceptable data types.
    """
    assert isinstance(y_pred, (tf.Tensor, torch.Tensor)), "only support tf.Tensor or torch.Tensor as y_pred"
    assert isinstance(y_true, (tf.Tensor, torch.Tensor)), "only support tf.Tensor or torch.Tensor as y_true"
    if tf.is_tensor(y_pred):
        ce = tf.losses.categorical_crossentropy(y_pred=y_pred, y_true=y_true, from_logits=from_logits)
        if class_weights is not None:
            sample_weights = class_weights.lookup(tf.math.argmax(y_true, axis=-1, output_type=class_weights.key_dtype))
            ce = ce * sample_weights
    else:
        y_true = y_true.to(torch.float)
        ce = _categorical_crossentropy_torch(y_pred=y_pred, y_true=y_true, from_logits=from_logits)
        if class_weights is not None:
            y_class = torch.argmax(y_true, dim=-1)
            sample_weights = torch.ones_like(y_class, dtype=torch.float)
            for key in class_weights.keys():
                sample_weights[y_class == key] = class_weights[key]
            ce = ce * sample_weights.reshape(ce.shape)

    if average_loss:
        ce = reduce_mean(ce)
    return ce


def _categorical_crossentropy_torch(y_pred: Tensor, y_true: Tensor, from_logits: bool) -> Tensor:
    if from_logits:
        ce = torch.sum(-y_true * torch.nn.LogSoftmax(dim=1)(y_pred), 1)
    else:
        ce = torch.sum(-y_true * torch.log(y_pred), 1)
    return ce
