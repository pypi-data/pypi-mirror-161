# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for different utility operations regarding time and json operations"""
import inspect
import json
from datetime import datetime, timedelta
from typing import Any


def get_current_timestamp(format_string: str = "%d-%b-%Y (%H:%M:%S.%f)") -> str:
    """
    Returns the current time in the given format
    Args:
        format_string: String, defining the format of the timestamp

    Returns: String, the formatted timestamp

    """

    timestamp = datetime.now()

    timestamp_string = timestamp.strftime(format_string)

    return timestamp_string


def timestamp_to_datetime(datetime_object: datetime) -> timedelta:
    """
    Transforms a timestamp to a timedelta based on the given object's attributes

    Args:
        datetime_object: datetime, a timestamp

    Returns: a timedelta object

    """

    return timedelta(
        hours=datetime_object.hour,
        minutes=datetime_object.minute,
        seconds=datetime_object.second,
        microseconds=datetime_object.microsecond,
    )


class CustomJSONEncoder(json.JSONEncoder):
    """Class for encoding json objects"""

    def default(self, obj: Any) -> Any:
        """
        Sets the class's default attribute to the json version of the given object

        Args:
            obj: Any, an object that should be transformed to json format

        Returns: Any, the given object without changes

        """

        if hasattr(obj, "to_json"):
            return self.default(obj.to_json())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj
