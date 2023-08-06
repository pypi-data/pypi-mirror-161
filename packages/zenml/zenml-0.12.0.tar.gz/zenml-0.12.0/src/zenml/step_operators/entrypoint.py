#  Copyright (c) ZenML GmbH 2022. All Rights Reserved.
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
"""Entrypoint for the step operator."""

import importlib
import logging
import sys
from typing import Dict, Type, cast

import click
from tfx.dsl.components.base.base_executor import BaseExecutor
from tfx.orchestration.portable.data_types import ExecutionInfo
from tfx.orchestration.portable.python_executor_operator import (
    run_with_executor,
)
from tfx.proto.orchestration.execution_invocation_pb2 import ExecutionInvocation

from zenml import constants
from zenml.artifacts.base_artifact import BaseArtifact
from zenml.artifacts.type_registry import type_registry
from zenml.integrations.registry import integration_registry
from zenml.io import fileio
from zenml.repository import Repository
from zenml.steps import BaseStep
from zenml.steps.utils import _FunctionExecutor, generate_component_class
from zenml.utils import source_utils, yaml_utils


def create_executor_class(
    step_source_path: str,
    input_artifact_type_mapping: Dict[str, str],
) -> Type[_FunctionExecutor]:
    """Creates an executor class for a given step.

    Args:
        step_source_path: Import path of the step to run.
        input_artifact_type_mapping: A dictionary mapping input names to
            a string representation of their artifact classes.

    Returns:
        A class of an executor instance.
    """
    step_class = cast(
        Type[BaseStep], source_utils.load_source_path_class(step_source_path)
    )
    step_instance = step_class()

    materializers = step_instance.get_materializers(ensure_complete=True)

    # We don't publish anything to the metadata store inside this environment,
    # so the specific artifact classes don't matter
    input_spec = {}
    for key, value in step_class.INPUT_SIGNATURE.items():
        input_spec[key] = BaseArtifact

    output_spec = {}
    for key, value in step_class.OUTPUT_SIGNATURE.items():
        output_spec[key] = type_registry.get_artifact_type(value)[0]

    execution_parameters = {
        **step_instance.PARAM_SPEC,
        **step_instance._internal_execution_parameters,
    }

    component_class = generate_component_class(
        step_name=step_instance.name,
        step_module=step_class.__module__,
        input_spec=input_spec,
        output_spec=output_spec,
        execution_parameter_names=set(execution_parameters),
        step_function=step_instance.entrypoint,
        materializers=materializers,
        enable_cache=step_instance.enable_cache,
    )

    return cast(
        Type[_FunctionExecutor], component_class.EXECUTOR_SPEC.executor_class
    )


def load_execution_info(execution_info_path: str) -> ExecutionInfo:
    """Loads the execution info from the given path.

    Args:
        execution_info_path: Path to the execution info file.

    Returns:
        Execution info.
    """
    with fileio.open(execution_info_path, "rb") as f:
        execution_info_proto = ExecutionInvocation.FromString(f.read())

    return ExecutionInfo.from_proto(execution_info_proto)


def configure_executor(
    executor_class: Type[BaseExecutor], execution_info: ExecutionInfo
) -> BaseExecutor:
    """Creates and configures an executor instance.

    Args:
        executor_class: The class of the executor instance.
        execution_info: Execution info for the executor.

    Returns:
        A configured executor instance.
    """
    context = BaseExecutor.Context(
        tmp_dir=execution_info.tmp_dir,
        unique_id=str(execution_info.execution_id),
        executor_output_uri=execution_info.execution_output_uri,
        stateful_working_dir=execution_info.stateful_working_dir,
        pipeline_node=execution_info.pipeline_node,
        pipeline_info=execution_info.pipeline_info,
        pipeline_run_id=execution_info.pipeline_run_id,
    )

    return executor_class(context=context)


@click.command()
@click.option("--main_module", required=True, type=str)
@click.option("--step_source_path", required=True, type=str)
@click.option("--execution_info_path", required=True, type=str)
@click.option("--input_artifact_types_path", required=True, type=str)
def main(
    main_module: str,
    step_source_path: str,
    execution_info_path: str,
    input_artifact_types_path: str,
) -> None:
    """Runs a single ZenML step.

    Args:
        main_module: The module containing the main function.
        step_source_path: Import path of the step to run.
        execution_info_path: Path to the execution info file.
        input_artifact_types_path: Path to the input artifact types file.
    """
    # prevent running entire pipeline in user code if they would run at import
    # time (e.g. not wrapped in a function or __name__== "__main__" check)
    constants.SHOULD_PREVENT_PIPELINE_EXECUTION = True

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    logging.getLogger().setLevel(logging.INFO)

    # activate integrations and import the user main module to register all
    # materializers and stack components
    integration_registry.activate_integrations()
    importlib.import_module(main_module)
    # create an instance of the active stack. This makes sure the artifact
    # store is created and registered in `fileio` so we can read the entrypoint
    # inputs
    stack = Repository().active_stack

    input_artifact_type_mapping = yaml_utils.read_json(
        input_artifact_types_path
    )
    executor_class = create_executor_class(
        step_source_path=step_source_path,
        input_artifact_type_mapping=input_artifact_type_mapping,
    )

    execution_info = load_execution_info(execution_info_path)
    executor = configure_executor(executor_class, execution_info=execution_info)

    stack.prepare_step_run()
    run_with_executor(execution_info=execution_info, executor=executor)
    stack.cleanup_step_run()


if __name__ == "__main__":
    main()
