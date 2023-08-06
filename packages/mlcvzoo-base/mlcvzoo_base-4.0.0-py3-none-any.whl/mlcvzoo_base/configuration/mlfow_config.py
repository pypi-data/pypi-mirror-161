# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Module for parsing information from yaml in python accessible attributes for using mlflow.
"""
from typing import Dict, List, Optional

import related
from config_builder.BaseConfigClass import BaseConfigClass


@related.mutable(strict=True)
class MLFlowPostgresSQLConfig(BaseConfigClass):
    """Class for parsing information about a SQL sever used for storing experiment information"""

    database_user: str = related.StringField()
    database_pw: str = related.StringField()
    database_port: str = related.StringField(default=5432)
    database_name: str = related.StringField(default="mlflowdb")


@related.mutable(strict=True)
class MLFlowFileConfig(BaseConfigClass):
    """Class for parsing information about a directory used for storing experiment information"""

    logging_dir: str = related.StringField()


@related.mutable(strict=True)
class MLFlowConfig(BaseConfigClass):
    """
    Class for parsing general information about path handling and also further
    configuration information in respective hierarchy
    """

    mutual_attribute_map: Dict[str, List[str]] = {
        "MLFlowConfig": [
            "mlflow_postgressql_config",
            "mlflow_file_config",
        ]
    }

    artifact_location: str = related.StringField()

    mlflow_postgressql_config: Optional[MLFlowPostgresSQLConfig] = related.ChildField(
        cls=MLFlowPostgresSQLConfig, required=False, default=None
    )

    mlflow_file_config: Optional[MLFlowFileConfig] = related.ChildField(
        cls=MLFlowFileConfig, required=False, default=None
    )
