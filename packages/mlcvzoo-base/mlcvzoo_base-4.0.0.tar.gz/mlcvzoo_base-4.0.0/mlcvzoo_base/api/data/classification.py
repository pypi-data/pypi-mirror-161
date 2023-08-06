# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""Data class that holds attributes of Classification objects"""

from __future__ import annotations

import math
from typing import Optional

from mlcvzoo_base.api.data.class_identifier import ClassIdentifier
from mlcvzoo_base.api.interfaces import Perception


class Classification(Perception):
    """
    Class which is used to state which object type is described by an given image.
    """

    # ClassIdentifier attribute that represents the primary class information
    # of a Classification object
    _class_identifier: ClassIdentifier

    # ClassIdentifier attribute that is used to store class information that has
    # been produced by a model. In most cases it is equal to the 'class_identifier',
    # but in cases where the class information of a models prediction has been
    # mapped / post processed, it can be used to access the real output of the model.
    _model_class_identifier: ClassIdentifier

    # score which expresses the likelihood that the class-id / class-name is correct
    __score: float

    def __init__(
        self,
        class_identifier: ClassIdentifier,
        score: float,
        model_class_identifier: Optional[ClassIdentifier] = None,
    ):
        self.__score = score
        self.__class_identifier = class_identifier

        if model_class_identifier is None:
            self.__model_class_identifier = class_identifier
        else:
            self.__model_class_identifier = model_class_identifier

    def __eq__(self, other: Classification) -> bool:  # type: ignore
        return (
            # 4 decimals should be plenty for accuracy
            math.isclose(a=self.score, b=other.score, abs_tol=0.0005)
            and self.__class_identifier.class_id == other.__class_identifier.class_id
            and self.__class_identifier.class_name == other.__class_identifier.class_name
            and self.__model_class_identifier.class_id == other.__model_class_identifier.class_id
            and self.__model_class_identifier.class_name
            == other.__model_class_identifier.class_name
        )

    def __repr__(self):  # type: ignore
        return (
            f"Classification("
            f"class-id={self.class_id}, "
            f"class-name={self.class_name}: "
            f"model-class-id={self.model_class_identifier.class_id}, "
            f"model-class-name={self.model_class_identifier.class_name}: "
            f"score={self.score})"
        )

    @property
    def class_identifier(self) -> ClassIdentifier:
        return self.__class_identifier

    @property
    def model_class_identifier(self) -> ClassIdentifier:
        return self.__model_class_identifier

    @property
    def class_id(self) -> int:
        return self.__class_identifier.class_id

    @property
    def class_name(self) -> str:
        return self.__class_identifier.class_name

    @property
    def score(self) -> float:
        return self.__score

    def copy_classification(self, class_identifier: ClassIdentifier) -> Classification:

        return Classification(
            class_identifier=class_identifier,
            score=self.score,
            model_class_identifier=self.model_class_identifier,
        )
