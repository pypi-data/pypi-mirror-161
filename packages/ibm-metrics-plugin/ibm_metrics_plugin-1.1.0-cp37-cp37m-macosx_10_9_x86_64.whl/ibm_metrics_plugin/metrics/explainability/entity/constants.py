# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2021, 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from enum import Enum


class ExplanationType(Enum):
    """Supported explanation"""
    LOCAL = "local"
    GLOBAL = "global"


class Status(Enum):
    """Enumerated type for status of the explanation."""
    NEW = "new"
    IN_PROGRESS = "in_progress"
    ERROR = "error"
    FINISHED = "finished"


class LimeFeatureSelection(Enum):
    """Supported Feature selection values"""
    AUTO = "auto"
    FORWARD_SELECTION = "forward_selection"
    LASSO_PATH = "lasso_path"
    HIGHEST_WEIGHTS = "highest_weights"
    NONE = "none"


class ShapAlgorithm(Enum):
    """Supported Shap algorithm values"""
    KERNEL = "kernel"
    TREE = "tree"


class ShapAggregationMethod(Enum):
    """Supported aggregation method for shap global explanations"""
    MEAN_ABS = "mean_abs"
    MEAN_SQ = "mean_sq"
    MAX_ABS = "max_abs"

    @staticmethod
    def values():
        return [e.value for e in ShapAggregationMethod]


class ImageHeuristic(Enum):
    """Enumerated type for different image heuristics.

        1. DEFAULT: Just take top 5 features based on weight.
        2. TOP_5_POSITIVE_TOP_5_NEGATIVE: Take top 5 positive and top 5 negative features based on weight.
        3. TOP_5_POSITIVE_TOP_5_NEGATIVE_THRESHOLD

    """
    DEFAULT = 0
    TOP_5_POSITIVE_TOP_5_NEGATIVE = 1
    TOP_5_POSITIVE_TOP_5_NEGATIVE_THRESHOLD = 2


FEATURES_COUNT = 10
