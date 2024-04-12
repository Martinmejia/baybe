"""Acquisition function wrappers."""

from baybe.acquisition.acqfs import (
    ExpectedImprovement,
    ProbabilityOfImprovement,
    UpperConfidenceBound,
    qExpectedImprovement,
    qProbabilityOfImprovement,
    qUpperConfidenceBound,
)
from baybe.acquisition.adapter import AdapterModel
from baybe.acquisition.partial import PartialAcquisitionFunction

EI = ExpectedImprovement
PI = ProbabilityOfImprovement
UCB = UpperConfidenceBound
qEI = qExpectedImprovement
qPI = qProbabilityOfImprovement
qUCB = qUpperConfidenceBound

__all__ = [
    # ---------------------------
    # Acquisition functions
    "ExpectedImprovement",
    "ProbabilityOfImprovement",
    "UpperConfidenceBound",
    "qExpectedImprovement",
    "qProbabilityOfImprovement",
    "qUpperConfidenceBound",
    # ---------------------------
    # Abbreviations
    "EI",
    "PI",
    "UCB",
    "qEI",
    "qPI",
    "qUCB",
    # ---------------------------
    # Helpers
    "AdapterModel",
    "PartialAcquisitionFunction",
]
