#  Copyright (c) ZenML GmbH 2021. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.
"""Implementation of ZenML's builtin materializer."""

import os
from typing import Any, Type

from zenml.artifacts import DataAnalysisArtifact, DataArtifact
from zenml.logger import get_logger
from zenml.materializers.base_materializer import BaseMaterializer
from zenml.utils import yaml_utils

logger = get_logger(__name__)
DEFAULT_FILENAME = "data.json"


class BuiltInMaterializer(BaseMaterializer):
    """Read/Write JSON files."""

    # since these are the 'correct' way to annotate these types.

    ASSOCIATED_ARTIFACT_TYPES = (
        DataArtifact,
        DataAnalysisArtifact,
    )
    ASSOCIATED_TYPES = (
        int,
        str,
        bytes,
        dict,
        float,
        list,
        tuple,
        bool,
    )

    def handle_input(self, data_type: Type[Any]) -> Any:
        """Reads basic primitive types from json.

        Args:
            data_type: The type of the data to read.

        Returns:
            The data read.
        """
        super().handle_input(data_type)
        filepath = os.path.join(self.artifact.uri, DEFAULT_FILENAME)
        contents = yaml_utils.read_json(filepath)
        if type(contents) != data_type:
            # TODO [ENG-142]: Raise error or try to coerce
            logger.debug(
                f"Contents {contents} was type {type(contents)} but expected "
                f"{data_type}"
            )
        return contents

    def handle_return(self, data: Any) -> None:
        """Handles basic built-in types and stores them as json.

        Args:
            data: The data to store.
        """
        super().handle_return(data)
        filepath = os.path.join(self.artifact.uri, DEFAULT_FILENAME)
        yaml_utils.write_json(filepath, data)
