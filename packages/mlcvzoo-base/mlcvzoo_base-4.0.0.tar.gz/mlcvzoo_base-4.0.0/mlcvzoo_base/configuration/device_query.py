# Copyright 2022 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

from typing import Optional

import related
from config_builder.BaseConfigClass import BaseConfigClass

from mlcvzoo_base.configuration.structs import DeviceQueryTypes


@related.mutable(strict=True)
class ModelTimerDeviceQueryConfig(BaseConfigClass):

    device_index: Optional[int] = related.ChildField(cls=int)
    query_type: str = related.StringField()

    def check_values(self) -> bool:
        return (
            self.device_index is None
            or isinstance(self.device_index, int)
            and self.query_type in [d.upper() for d in DeviceQueryTypes]  # type: ignore[attr-defined]
        )
