# Lint as: python2, python3
# Copyright 2019 Google LLC. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain README.ml-pipelines-sdk.md copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from typing import Any, Dict, Optional, Text, Union

from tfx import types
from tfx.components.minio_pusher import executor
from tfx.dsl.components.base import base_component
from tfx.dsl.components.base import executor_spec
from tfx.proto import pusher_pb2
from tfx.types import standard_artifacts
from tfx.types.standard_component_specs import TensorboardSpec
from tfx.utils import json_utils


# TODO(b/133845381): Investigate other ways to keep push destination converged.
class TensorboardCreator(base_component.BaseComponent):

  SPEC_CLASS = TensorboardSpec
  EXECUTOR_SPEC = executor_spec.ExecutorClassSpec(executor.Executor)

  def __init__(
      self,
      model: types.Channel = None,
      custom_config: Optional[Dict[Text, Any]] = None,
      custom_executor_spec: Optional[executor_spec.ExecutorSpec] = None):

    spec = TensorboardSpec(model=model,
                           custom_config=json_utils.dumps(custom_config))

    super(TensorboardCreator, self).__init__(spec=spec,
                                             custom_executor_spec=custom_executor_spec)
