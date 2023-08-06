# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

"""
Definition of interfaces / abstract classes that define additional features of mlcvzoo models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Generic, Optional, TypeVar

from mlcvzoo_base.api.data.annotation_class_mapper import AnnotationClassMapper

NetType = TypeVar("NetType")


@dataclass
class Perception:
    """
    Base class for representing any data object which is consumed by
    models of the MLCVZoo. This includes ground-truth data as well as
    predicted objects. Dataclasses should inherit from this class in
    order to be used in a predict(...) method of the model class,
    or sub-classes of the model class e.g. for any object detector,
    character classifier, OCR, etc.
    """


class Classifiable(ABC):
    """
    A model that inherits from the Classifiable interface states that its prediction
    output is representing some kind of class instance. A class in this context means
    real world instance like person, car, truck, cat, ... etc.
    """

    def __init__(self, mapper: AnnotationClassMapper):
        self._mapper = mapper

    @property
    def mapper(self) -> AnnotationClassMapper:
        """
        Returns:
            The mapper object associated with this classifiable model
        """
        return self._mapper

    @property
    def num_classes(self) -> int:
        """
        Returns:
            The number of classes for which this model is build.
        """
        raise NotImplementedError("Must be implemented by sub-class: num_classes(...).")

    def get_classes_id_dict(self) -> Dict[int, str]:
        """
        The prediction output of classifiable models contains representations of classes
        as IDs. These IDs are associated with real world instances like car, truck, person etc.
        Therefore each classifiable model has to provide a dictionary that indicates how the
        class IDs are mapped to class names.

        Returns:
            The dictionary that indicates the mapping of class IDs to class names
        """
        raise NotImplementedError("Must be implemented by sub-class: get_classes_id_dict(...).")


class Trainable(ABC):
    """
    The interface represents the super-class for any trainable model.
    A trainable model must not necessarily be a model based on
    an neural network. A trainable model could also be an algorithm like
    any reinforcement algorithm for example.
    """

    @abstractmethod
    def train(self) -> None:
        """
        The method trains the model.

        Sub-classes must implement the training, including proper use of the
        model configuration and parameters.

        Returns:
            None
        """
        raise NotImplementedError("Must be implemented by sub-class: train(...).")


class NetBased(ABC, Generic[NetType]):
    """
    The interface represents the super-class for any net based model. The term "net"
    in this context is associated with any kind of neural network.
    """

    def __init__(self, net: Optional[NetType]):
        self.net: Optional[NetType] = net

    def get_net(self) -> Optional[NetType]:
        """
        Returns:
            An instance of the net used in this model.
        """
        return self.net

    @abstractmethod
    def store(self, checkpoint_path: str) -> None:
        """
        The method stores the weights of the net in the given checkpoint path
        """
        raise NotImplementedError("Must be implemented by sub-class: store(...)")

    @abstractmethod
    def restore(self, checkpoint_path: str) -> None:
        """
        The method restores the weights of the net from the given checkpoint path

        """
        raise NotImplementedError("Must be implemented by sub-class: restore(...)")
