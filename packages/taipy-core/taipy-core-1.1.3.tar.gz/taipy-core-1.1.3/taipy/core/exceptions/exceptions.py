# Copyright 2022 Avaiga Private Limited
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with
# the License. You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on
# an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.


class LoadingError(Exception):
    """Raised if an error occurs while loading the configuration file."""


class ConfigurationIssueError(Exception):
    """Raised if an inconsistency has been detected in the configuration."""


class InconsistentEnvVariableError(Exception):
    """Inconsistency value has been detected in an environment variable referenced by the configuration."""


class MissingEnvVariableError(Exception):
    """Environment variable referenced in configuration is missing."""


class InvalidConfigurationId(Exception):
    """Configuration id is not valid."""


class CycleAlreadyExists(Exception):
    """Raised if it is trying to create a Cycle that has already exists."""


class NonExistingCycle(Exception):
    """Raised if we request a cycle not known by the cycle manager."""


class MissingRequiredProperty(Exception):
    """Raised if a required property is missing when creating a Data Node."""


class InvalidDataNodeType(Exception):
    """Raised if a data node storage type does not exist."""


class MultipleDataNodeFromSameConfigWithSameParent(Exception):
    """
    Raised if there are multiple data nodes from the same data node configuration and the same parent identifier.
    """


class NoData(Exception):
    """Raised if a data node is read before it has been written.

    This exception can be raised by `DataNode.read_or_raise()^`.
    """


class UnknownDatabaseEngine(Exception):
    """Raised if the database engine is not known when creating a connection with a SQLDataNode."""


class NonExistingDataNode(Exception):
    """Raised if a requested DataNode is not known by the DataNode Manager."""

    def __init__(self, data_node_id: str):
        self.message = f"DataNode: {data_node_id} does not exist."


class NonExistingExcelSheet(Exception):
    """Raised if a requested Sheet name does not exist in the provided Excel file."""

    def __init__(self, sheet_name: str, excel_file_name: str):
        self.message = f"{sheet_name} does not exist in {excel_file_name}."


class NotMatchSheetNameAndCustomObject(Exception):
    """Raised if a provided list of sheet names does not match with the provided list of custom objects."""


class MissingReadFunction(Exception):
    """Raised if no read function is provided for the GenericDataNode."""


class MissingWriteFunction(Exception):
    """Raised if no write function is provided for the GenericDataNode."""


class JobNotDeletedException(RuntimeError):
    """Raised if we try to delete a job that cannot be deleted.

    This exception can be raised by `taipy.delete_job()^`.
    """

    def __init__(self, job_id: str):
        self.message = f"Job: {job_id} cannot be deleted."


class NonExistingJob(RuntimeError):
    """Raised if we try to get a job that does not exist."""

    def __init__(self, job_id: str):
        self.message = f"Job: {job_id} does not exist."


class DataNodeWritingError(RuntimeError):
    """Raised if an error happens during the writing in a data node."""


class InvalidSubscriber(RuntimeError):
    """Raised if we try to load a function that is not valid."""


class NonExistingPipeline(Exception):
    """Raised if a requested Pipeline is not known by the Pipeline Manager."""

    def __init__(self, pipeline_id: str):
        self.message = f"Pipeline: {pipeline_id} does not exist."


class NonExistingPipelineConfig(Exception):
    """Raised if a requested Pipeline configuration is not known by the Pipeline Manager."""

    def __init__(self, pipeline_config_id: str):
        self.message = f"Pipeline config: {pipeline_config_id} does not exist."


class MultiplePipelineFromSameConfigWithSameParent(Exception):
    """Raised if it exists multiple pipelines from the same pipeline config and with the same _parent_id_."""


class ModelNotFound(Exception):
    """Raised when trying to fetch a non-existent model.

    This exception can be raised by `taipy.get()^` and `taipy.delete()^`.
    """

    def __init__(self, model_name: str, model_id: str):
        self.message = f"A {model_name} model with id {model_id} could not be found."


class NonExistingScenario(Exception):
    """Raised if a requested scenario is not known by the Scenario Manager."""

    def __init__(self, scenario_id: str):
        self.message = f"Scenario: {scenario_id} does not exist."


class NonExistingScenarioConfig(Exception):
    """Raised if a requested scenario configuration is not known by the Scenario Manager.

    This exception can be raised by `taipy.compare_scenarios()^`.
    """

    def __init__(self, scenario_config_id: str):
        self.message = f"Scenario config: {scenario_config_id} does not exist."


class DoesNotBelongToACycle(Exception):
    """Raised if a scenario without any cycle is promoted as primary scenario."""


class DeletingPrimaryScenario(Exception):
    """Raised if a primary scenario is deleted."""


class DifferentScenarioConfigs(Exception):
    """Raised if scenario comparison is requested on scenarios with different scenario configs.

    This exception can be raised by `taipy.compare_scenarios()^`.
    """


class InsufficientScenarioToCompare(Exception):
    """Raised if too few scenarios are requested to be compared.

    Scenario comparison need at least two scenarios to compare.

    This exception can be raised by `taipy.compare_scenarios()^`.
    """


class NonExistingComparator(Exception):
    """Raised if a scenario comparator does not exist.

    This exception can be raised by `taipy.compare_scenarios()^`.
    """


class UnauthorizedTagError(Exception):
    """Must provide an authorized tag."""


class DependencyNotInstalled(Exception):
    """Raised if a package is missing."""

    def __init__(self, package_name: str):
        self.message = f"""
        Package '{package_name}' should be installed.
        Run 'pip install taipy[{package_name}]' to installed it.
        """


class NonExistingTask(Exception):
    """Raised if a requested task is not known by the Task Manager."""

    def __init__(self, task_id: str):
        self.message = f"Task: {task_id} does not exist."


class NonExistingTaskConfig(Exception):
    """Raised if a requested task configuration is not known by the Task Manager."""

    def __init__(self, id: str):
        self.message = f"Task config: {id} does not exist."


class MultipleTaskFromSameConfigWithSameParent(Exception):
    """Raised if there are multiple tasks from the same task configuration and the same parent identifier."""


class ModeNotAvailable(Exception):
    """Raised if the mode in JobConfig is not supported."""
