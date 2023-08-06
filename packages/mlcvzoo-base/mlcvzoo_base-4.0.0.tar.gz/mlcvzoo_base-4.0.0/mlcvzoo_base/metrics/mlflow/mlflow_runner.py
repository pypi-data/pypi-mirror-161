# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for using MLFlow tool in MLCVZoo"""
import copy
import logging
import re
import typing
from typing import Dict, List, Optional

import mlflow
from config_builder import ConfigBuilder
from mlflow import ActiveRun
from mlflow.entities import Experiment

from mlcvzoo_base.configuration.mlfow_config import MLFlowConfig
from mlcvzoo_base.configuration.structs import (
    MLFlowExperimentConfig,
    MLFLowTrackingUriTypes,
)

logger = logging.getLogger(__name__)


class MLFLowRunner:
    """
    Class for wrapping the start and stop of mlflow runs
    """

    def __init__(
        self,
        configuration: Optional[MLFlowConfig] = None,
        yaml_config_path: Optional[str] = None,
        string_replacement_map: Optional[Dict[str, str]] = None,
        mutual_attribute_map: Optional[Dict[str, List[str]]] = None,
        no_checks: bool = False,
        create_experiments: bool = True,
    ):
        """
        Init with all parameters that can be set for the config-builder.

        Args:
            configuration:
            yaml_config_path:
            string_replacement_map:
            mutual_attribute_map:
            no_checks:
            create_experiments:

        Returns:
            The created object
        """

        self.mlflow_run: Optional[ActiveRun] = None
        self.artifact_location: Optional[str] = None

        # Build configuration by instantiating a config-builder object
        config_builder = ConfigBuilder(
            class_type=MLFlowConfig,
            configuration=configuration,
            yaml_config_path=yaml_config_path,
            string_replacement_map=string_replacement_map,
            mutual_attribute_map=mutual_attribute_map,
            no_checks=no_checks,
        )

        self.configuration: MLFlowConfig = typing.cast(
            MLFlowConfig, copy.deepcopy(config_builder.configuration)
        )

        # Setup base experiments
        if create_experiments:
            self.create_mlflow_experiments()

    def create_mlflow_experiments(self) -> None:
        """
        Create all mlflow experiments that are specified in MLFlowExperimentConfig.EXPERIMENT_DICT.
        Init according to the configured backed
        -> mlflow_file_config        => setup mlflow to write data to local directory
        -> mlflow_postgressql_config => setup mlflow to write to postgresql database

        :return:
        """

        if self.configuration.mlflow_file_config is not None:
            mlflow.set_tracking_uri(
                f"{MLFLowTrackingUriTypes.FILE}:{self.configuration.mlflow_file_config.logging_dir}"
            )

        elif self.configuration.mlflow_postgressql_config is not None:

            DB_USER = self.configuration.mlflow_postgressql_config.database_user
            DB_PW = self.configuration.mlflow_postgressql_config.database_pw
            DB_PORT = self.configuration.mlflow_postgressql_config.database_port
            DB_NAME = self.configuration.mlflow_postgressql_config.database_name

            mlflow.set_tracking_uri(
                f"{MLFLowTrackingUriTypes.POSTGRES}://{DB_USER}:{DB_PW}@localhost:{DB_PORT}/{DB_NAME}"
            )
        else:
            logger.error("No valid configuration given, could not create an mlflow experiment")
            return

        for (
            experiment_id,
            experiment_name,
        ) in MLFlowExperimentConfig.EXPERIMENT_DICT.items():

            try:
                mlflow_experiment_id = mlflow.create_experiment(
                    name=experiment_name,
                    artifact_location=self.configuration.artifact_location,
                )

                logger.info(
                    f"Created Experiment: "
                    f"ID={mlflow_experiment_id}, "
                    f"NAME={experiment_name}, "
                    f"ARTIFACT_LOCATION={self.configuration.artifact_location}"
                )
            except mlflow.exceptions.MlflowException as e:

                reg_search = re.search(
                    pattern="already exist",
                    string=str(e),
                    flags=re.M | re.I,
                )

                if reg_search is not None:
                    logger.debug(f"Ignore MlflowException: {str(e)}")
                else:
                    logger.exception(e)

    @staticmethod
    def end_run() -> None:
        """
        Terminate mlflow run (if there is one).
        Catch known errors
        """
        try:
            mlflow.end_run()
        except mlflow.exceptions.MlflowException as mlflow_exception:
            logger.warning(mlflow_exception)

    def start_mlflow_run(
        self,
        run_id: Optional[str] = None,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None,
        end_runs_in_advance: bool = True,
    ) -> Optional[str]:
        """
        Start an mlflow run. Two options:
        1) By run-id, this will continue the run with the specified ID
        2) By experiment- and run-name

        :param experiment_name:
        :param run_name:
        :param run_id:
        :param end_runs_in_advance:
        :return:
        """

        # Ensure that no other mlflow run is started
        if end_runs_in_advance:
            MLFLowRunner.end_run()

        # Use run-id and continue mlflow run
        if run_id is not None:
            try:
                self.mlflow_run = mlflow.start_run(run_id=run_id)

                logger.info(
                    "=========================================\n"
                    f"Continue mlflow run:\n{self.mlflow_run}\n"
                )

                return str(self.mlflow_run.info.run_id)

            except mlflow.exceptions.MlflowException:
                logger.warning(
                    f"Could not continue mlflow run with run-id {run_id}. Start new mlflow run ..."
                )

        # start new mlflow run with given experiment_name and run_name
        elif experiment_name is not None and run_name is not None:

            mlflow_experiment: Optional[Experiment]

            if experiment_name in MLFlowExperimentConfig.EXPERIMENT_DICT.values():
                mlflow_experiment = mlflow.get_experiment_by_name(name=experiment_name)
            else:
                logger.error(
                    "experiment-name is not valid. "
                    f"Provide one of {MLFlowExperimentConfig.EXPERIMENT_DICT.values()}"
                )
                return None

            if mlflow_experiment is not None:
                self.mlflow_run = mlflow.start_run(
                    experiment_id=mlflow_experiment.experiment_id, run_name=run_name
                )

                logger.info(
                    "=========================================\n"
                    f"New mlflow run: \n{self.mlflow_run.info}\n"
                )

                return str(self.mlflow_run.info.run_id)
            else:
                logger.error(
                    f"Could not start a mlflow run for experiment-name '{experiment_name}'"
                )

        return None
