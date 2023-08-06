# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Module for handling implicit replacements"""

__author__ = "Oliver Bredtmann"
__license__ = "Open Logistics License 1.0"
__email__ = "Oliver.Bredtmann@dbschenker.com"

import os


class ImplicitReplacement:
    """
    Save replacement of
        - directories
        - strings
    """

    ALL = "all"
    FIRST = "first"
    LAST = "last"
    HOW = [ALL, FIRST, LAST]

    @staticmethod
    def replace_directory_in_path(
        file_path: str, replacement_key: str, replacement_value: str, how: str = ALL
    ) -> str:
        """
        Replaces directory in the given path.

        Args:
            file_path: String, a path to a file
            replacement_key: String, defining what is about to be replaced
            replacement_value: String, defining what the replacement looks like
            how: String, one of ImplicitReplacement enums [ALL, FIRST, LAST]

        Returns: String, the updated file path

        """

        assert how in ImplicitReplacement.HOW

        path_list = os.path.normpath(file_path).split(os.sep)

        if how == ImplicitReplacement.ALL:
            path_list = list(
                map(
                    lambda x: x if x != replacement_key else replacement_value,
                    path_list,
                )
            )

        elif how == ImplicitReplacement.FIRST:
            for idx in range(len(path_list)):
                if path_list[idx] == replacement_key:
                    path_list[idx] = replacement_value
                    break

        elif how == ImplicitReplacement.LAST:
            for idx in list(range(len(path_list)))[::-1]:
                if path_list[idx] == replacement_key:
                    path_list[idx] = replacement_value
                    break

        new_path = os.sep.join(path_list)

        return new_path

    @staticmethod
    def replace_string_in_path(
        file_path: str, value: str, replacement_value: str, how: str = ALL
    ) -> str:
        """
        Replaces a string in the given path.

        Args:
            file_path: String, a path to a file
            value: String, defining what is about to be replaced
            replacement_value: String, defining what the replacement looks like
            how:

        Returns: String, one of ImplicitReplacement enums [ALL, FIRST, LAST]

        """

        assert how in ImplicitReplacement.HOW

        new_path = file_path
        if how == ImplicitReplacement.ALL:
            new_path = file_path.replace(value, replacement_value)

        elif how == ImplicitReplacement.FIRST:
            new_path = file_path.replace(value, replacement_value, 1)

        elif how == ImplicitReplacement.LAST:
            new_path = (file_path[::-1].replace(value[::-1], replacement_value[::-1], 1))[::-1]

        return new_path
