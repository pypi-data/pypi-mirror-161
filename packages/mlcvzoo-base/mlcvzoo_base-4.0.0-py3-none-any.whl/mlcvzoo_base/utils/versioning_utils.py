# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for defining methods that handle everything that
is related to versioning and dependencies of software.
"""
import logging
from typing import List, Tuple

import git

logger = logging.getLogger(__name__)


try:
    # pylint: disable=protected-access
    from pip._internal.operations import freeze
except ImportError:  # pip < 10.0
    from pip.operations import freeze  # type: ignore


def get_installed_pip_package_versions() -> List[str]:
    """
    Get versions of installed pip packages.
    """

    pip_packages = list(freeze.freeze())

    return pip_packages


def get_git_info() -> Tuple[str, str, str]:
    """
    Get info about the current git repository

    Returns:
        Tuple consisting of
        - repository identifier
        - sha as string
        - branch-name as string
    """

    repo = git.Repo(search_parent_directories=True)

    sha: str = str(repo.head.object.hexsha)

    try:
        branch: str = str(repo.active_branch)
    except TypeError as type_error:
        branch = str(type_error)

    return str(repo), sha, branch


def write_pip_info_to_file(output_requirements_path: str) -> None:
    """

    Args:
        output_requirements_path:

    Returns:

    """

    with open(file=output_requirements_path, mode="w") as pip_package_file:
        logger.info(
            "Write info about current installed pip package versions to file: %s",
            pip_package_file,
        )

        pip_packages = get_installed_pip_package_versions()
        for pip_package in pip_packages:
            pip_package_file.write(f"{pip_package}\n")
