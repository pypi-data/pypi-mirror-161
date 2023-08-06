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

import os
import time
from typing import Any, Dict, List, Optional, Text

from absl import logging
from tfx import types
from tfx.components.util import model_utils
from tfx.dsl.components.base import base_executor
from tfx.dsl.io import fileio
from tfx.proto import pusher_pb2
from tfx.types import artifact_utils
from tfx.types import standard_component_specs
from tfx.utils import io_utils
from tfx.utils import path_utils
from tfx.utils import proto_utils

##### Yulong start 20220803 #####
import time
import kubernetes.client
from kubernetes import config
config.load_incluster_config()
import json

##### Yulong end 20220803 #####


class Executor(base_executor.BaseExecutor):

  def Do(self, input_dict: Dict[Text, List[types.Artifact]],
         output_dict: Dict[Text, List[types.Artifact]],
         exec_properties: Dict[Text, Any]) -> None:

    custom_config = json.loads(exec_properties.get("custom_config"))
    namespace = custom_config["namespace"]
    tb_name = custom_config["tensorboard_name"]

    model_export = artifact_utils.get_single_instance(
      input_dict[standard_component_specs.MODEL_KEY])
    model_path = path_utils.serving_model_path(model_export.uri)
    logs_uri = model_path + "/logs"
    # logs_uri = "s3://tfx/rflow-test/omnicare-sentiment-minio/Trainer/model/535/logs"

    config.load_incluster_config()
    api = kubernetes.client.CustomObjectsApi()

    tensorboard_obj = {
      "apiVersion": "tensorboard.kubeflow.org/v1alpha1",
      "kind": "Tensorboard",
      "metadata": {"name": tb_name, "namespace": namespace},
      "spec": {
        "logspath": logs_uri
      }
    }

    api.create_namespaced_custom_object(
      group="tensorboard.kubeflow.org",
      version="v1alpha1",
      namespace=namespace,
      plural="tensorboards",
      body=tensorboard_obj,
    )

    print("Tensorboard created")
