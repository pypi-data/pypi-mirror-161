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
from typing import TYPE_CHECKING

import lazy_loader as lazy

__getattr__, __dir__, __all__ = lazy.attach(__name__,
                                            submod_attrs={'fuse': ['Fuse'],
                                                          'one_of': ['OneOf'],
                                                          'repeat': ['Repeat'],
                                                          'sometimes': ['Sometimes'],
                                                          })

if TYPE_CHECKING:
    from fastestimator.op.tensorop.meta.fuse import Fuse
    from fastestimator.op.tensorop.meta.one_of import OneOf
    from fastestimator.op.tensorop.meta.repeat import Repeat
    from fastestimator.op.tensorop.meta.sometimes import Sometimes
