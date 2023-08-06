# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

import os
from dataclasses import dataclass
from subprocess import PIPE, Popen
from typing import Any, Callable, Dict, List, Optional

from mlcvzoo_base.configuration.device_query import ModelTimerDeviceQueryConfig
from mlcvzoo_base.configuration.structs import DeviceQueryTypes


@dataclass
class GpuInfo:
    """
    Datawrapper class for wrapping the information returned by the nvidia-smi command line tool.
    """

    id: int = 0
    uuid: str = ""
    load: float = 0.0
    memory_util: float = 0.0
    memory_total: float = 0.0
    memory_used: float = 0.0
    memory_free: float = 0.0
    driver: str = ""
    name: str = ""
    serial: str = ""
    display_mode: str = ""
    display_active: str = ""
    temperature: float = 0.0


def _cast_to_float(number_str: str) -> float:
    try:
        number = float(number_str)
    except ValueError:
        number = float("nan")
    return number


def _create_gpu_info_setter(
    conversion_func: Callable[[str], Any]
) -> Callable[[GpuInfo, str, Any], None]:
    """
    Args:
        conversion_func: function for converting the input value to the correct
        datatype when setting the respective attribute

    Returns:
        Callable for setting an attribute with name 'attr_name' in
        'gpu_info' to 'conversion_func(value)'
    """

    def _setter(gpu_info: GpuInfo, attr_name: str, value: Any) -> None:
        setattr(gpu_info, attr_name, conversion_func(value))

    return _setter


def get_nvidia_smi_info() -> List[GpuInfo]:
    """
    Query the system for gpu information via nvidia-smi command line tool.

    Returns:
        List of GpuInfo object containing information for the respective gpu.
    """

    query_gpu_dict: Dict[str, Dict[str, Any]] = {
        "index": {
            "attr_name": "id",
            "attr_setter": _create_gpu_info_setter(lambda x: int(x)),
        },
        "uuid": {
            "attr_name": "uuid",
            "attr_setter": _create_gpu_info_setter(lambda x: x),
        },
        "utilization.gpu": {
            "attr_name": "load",
            "attr_setter": _create_gpu_info_setter(lambda x: _cast_to_float(x) / 100),
        },
        "memory.total": {
            "attr_name": "memory_total",
            "attr_setter": _create_gpu_info_setter(lambda x: _cast_to_float(x)),
        },
        "memory.used": {
            "attr_name": "memory_used",
            "attr_setter": _create_gpu_info_setter(lambda x: _cast_to_float(x)),
        },
        "memory.free": {
            "attr_name": "memory_free",
            "attr_setter": _create_gpu_info_setter(lambda x: _cast_to_float(x)),
        },
        "driver_version": {
            "attr_name": "driver",
            "attr_setter": _create_gpu_info_setter(lambda x: x),
        },
        "name": {
            "attr_name": "name",
            "attr_setter": _create_gpu_info_setter(lambda x: x),
        },
        "gpu_serial": {
            "attr_name": "serial",
            "attr_setter": _create_gpu_info_setter(lambda x: x),
        },
        "display_active": {
            "attr_name": "display_active",
            "attr_setter": _create_gpu_info_setter(lambda x: x),
        },
        "display_mode": {
            "attr_name": "display_mode",
            "attr_setter": _create_gpu_info_setter(lambda x: x),
        },
        "temperature.gpu": {
            "attr_name": "temperature",
            "attr_setter": _create_gpu_info_setter(lambda x: _cast_to_float(x)),
        },
    }

    query_gpu_str: str = ",".join(query_gpu_dict.keys())

    try:
        p = Popen(
            [
                "nvidia-smi",
                f"--query-gpu={query_gpu_str}",
                "--format=csv,noheader,nounits",
            ],
            stdout=PIPE,
        )
        stdout, stderr = p.communicate()
    except (RuntimeError, FileNotFoundError):
        # nvidia-smi is not available / has an error, therefore return an empty list
        return []

    smi_output: str = stdout.decode("UTF-8")
    smi_lines: List[str] = smi_output.split(os.linesep)

    num_devices: int = len(smi_lines) - 1
    gpu_infos: List[GpuInfo] = []

    for device_num in range(num_devices):
        line: str = smi_lines[device_num]
        vals: List[str] = line.split(", ")

        gpu_info = GpuInfo()

        for i, key in enumerate(query_gpu_dict):
            attr_name: str = query_gpu_dict[key]["attr_name"]
            value: str = vals[i]
            setter: Callable[[GpuInfo, str, Any], None] = query_gpu_dict[key]["attr_setter"]

            setter(gpu_info, attr_name, value)

        gpu_info.memory_util = float(gpu_info.memory_used) / float(gpu_info.memory_total)
        gpu_infos.append(gpu_info)

    return gpu_infos


def get_device_info(device_query: ModelTimerDeviceQueryConfig) -> Optional[GpuInfo]:
    """
    Determine device information based on the given device query object

    Args:
        device_query: The device query object that should be used
                      to determine the device information

    Returns:
        The device information in form of a GpuInfo object
    """

    gpu_info: Optional[GpuInfo] = None
    if device_query.query_type == DeviceQueryTypes.NVIDIA_SMI.upper():  # type: ignore[attr-defined]

        gpu_info_list: List[GpuInfo] = get_nvidia_smi_info()
        if len(gpu_info_list) != 0:
            if device_query.device_index is not None:
                gpu_info = gpu_info_list[device_query.device_index]
            else:
                gpu_info = gpu_info_list[0]

    return gpu_info


if __name__ == "__main__":
    infos: List[GpuInfo] = get_nvidia_smi_info()

    import pprint

    pprint.pprint(infos)
