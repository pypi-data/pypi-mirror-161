# Copyright 2021 Open Logistics Foundation
#
# Licensed under the Open Logistics License 1.0.
# For details on the licensing terms, see the LICENSE file.

# TODO: Consider naming this "TextPerception" instead
"""Module for handling attributes of OCR objects"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

import numpy as np

from mlcvzoo_base.api.interfaces import Perception

DEFAULT_SCORE: float = 1.0


@dataclass
class OCRPerception(Perception):
    """Dataclass that holds attributes of OCR objects"""

    # Result of the OCR. Not all methods will recognize spaces correctly
    # so this may very well be exactly one word.
    words: List[str] = field(default_factory=list, repr=False)
    # Scores that correspond to 'predicted_words'
    word_scores: List[float] = field(default_factory=list, repr=False)
    # A chain of individual strings
    content: str = field(default="", repr=False)
    # Score of the whole prediction
    score: float = field(default=DEFAULT_SCORE, repr=False)

    def __post_init__(self) -> None:
        """
        Method to be called after instantiating an OCRPerception object.

        If the OCRModel has no text recognized return an
        OCRPerception with empty string content and empty list words.

        Returns:

        """
        if len(self.words) > 0:
            if len(self.word_scores) == 0:
                self.word_scores = [DEFAULT_SCORE for _ in self.words]
            elif self.score == DEFAULT_SCORE:
                # Convention: if not provided otherwise, the score is the mean of the word scores.
                self.score = float(np.mean(self.word_scores))
            if len(self.content) == 0:
                self.content = self.clean()
        elif len(self.content) > 0:
            self.words = [self.content]
            self.word_scores = [self.score]

    def __repr__(self) -> str:

        return f"OCRPerception({self.words} - {self.word_scores})"

    def __lt__(self, other: OCRPerception) -> bool:
        return self.score < other.score

    def to_dict(self) -> Dict[Any, Any]:
        return self.__dict__

    @staticmethod
    def from_dict(from_dict: Dict[Any, Any]) -> OCRPerception:
        """
        Instantiate a new object and update it's data
        with the information that is fed in via the
        from_dict variable

        Returns:
            the created OCRPerception object
        """

        perception = OCRPerception()

        for key in perception.__dict__.keys():
            perception.__dict__[key] = from_dict[key]

        return perception

    def clean(self, separator: str = " ") -> str:
        """
        Create a clean concatenated string that is build by the
        words of the ocr perception and a given separator

        Returns:
            the created string
        """

        return f"{separator}".join(self.words)

    def chain(self) -> str:
        """
        Convenience method to create a concatenation of words
        with an empty separator

        Returns:
            the created string
        """

        return self.clean(separator="")
