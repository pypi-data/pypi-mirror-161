# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

import logging
import os

import mlflow
from config_builder import BaseConfigClass

from mlcvzoo_base.configuration.utils import write_config_to_yaml
from mlcvzoo_base.utils.versioning_utils import get_git_info, write_pip_info_to_file

logger = logging.getLogger(__name__)


def mlflow_log_config_to_yaml(config: BaseConfigClass, output_yaml_config_path: str) -> None:
    """
    Save a given configuration to a yaml-file and log it to mlflow if specified

    Args:
        config:
        output_yaml_config_path:

    Returns:

    """

    write_config_to_yaml(config=config, output_yaml_config_path=output_yaml_config_path)

    if os.path.isfile(output_yaml_config_path):
        mlflow.log_artifact(
            local_path=output_yaml_config_path,
        )


def mlflow_log_pip_package_versions(output_requirements_path: str) -> None:
    """

    Args:
        output_requirements_path:

    Returns:

    """

    write_pip_info_to_file(output_requirements_path=output_requirements_path)

    if os.path.isfile(output_requirements_path):
        mlflow.log_artifact(
            local_path=output_requirements_path,
        )


def mlflow_log_git_info() -> None:
    """
    Log all git related information about the current project with mlflow

    Returns:

    """

    repo, sha, branch = get_git_info()

    mlflow.log_param(key="git_repo", value=str(repo))
    mlflow.log_param(key="git_sha", value=sha)
    mlflow.log_param(key="git_branch", value=str(branch))
