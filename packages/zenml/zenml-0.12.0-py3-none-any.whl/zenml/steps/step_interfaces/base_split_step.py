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
"""Base split step."""

from abc import abstractmethod

from zenml.artifacts import DataArtifact
from zenml.steps import BaseStep, BaseStepConfig, Output, StepContext


class BaseSplitStepConfig(BaseStepConfig):
    """Base class for split configs to inherit from."""


class BaseSplitStep(BaseStep):
    """Base step implementation for any split step implementation."""

    @abstractmethod
    def entrypoint(  # type: ignore[override]
        self,
        dataset: DataArtifact,
        config: BaseSplitStepConfig,
        context: StepContext,
    ) -> Output(  # type:ignore[valid-type]
        train=DataArtifact, test=DataArtifact, validation=DataArtifact
    ):
        """Entrypoint for a function for the split steps to run.

        Args:
            dataset: The dataset to split.
            config: The configuration for the step.
            context: The context for the step.

        Returns:
            The split datasets.
        """
