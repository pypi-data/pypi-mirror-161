# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2021, 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
from sklearn.exceptions import DataConversionWarning
import warnings
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from ibm_metrics_plugin.metrics.explainability.entity.training_stats import TrainingStats

from ibm_metrics_plugin.common.utils.constants import ProblemType, InputDataType
from ibm_metrics_plugin.metrics.explainability.entity.explain_config import ExplainConfig

warnings.filterwarnings("ignore", category=DataConversionWarning)


class TrainingData():
    """Class representing the training data of the model with details of training data and statistics derived from it"""

    def __init__(self, explain_config: ExplainConfig):
        if explain_config.input_data_type != InputDataType.STRUCTURED:
            return

        self.config = explain_config
        use_stats = self.__get_use_stats()
        self.explain_stats = self.config.training_stats if use_stats else None
        data_stats = TrainingDataStats(
            self.config.training_stats) if use_stats else self.__get_stats()

        self.computed_stats = ComputeStats(
            data_stats, self.config.features, self.config.categorical_features, self.config.features_schema, self.config.problem_type)

    def __get_use_stats(self):
        """Returns True if training statistics from configuration is to be used, False otherwise"""
        use_stats = False
        stats = self.config.training_stats
        input_data_type = self.config.input_data_type

        if stats is not None:
            use_stats = True
        elif self.config.training_data is None and stats is None and input_data_type is InputDataType.STRUCTURED:
            raise Exception(
                "Either training data or training data stats are required.")
        return use_stats

    def __get_stats(self):
        """Generates stats using training_data if stats are not available"""
        data_frame = self.__get_data_frame()

        training_data_info = {
            "label_column": self.config.label_column,
            "feature_columns": self.config.features,
            "categorical_columns": self.config.categorical_features,
            "problem_type": self.config.problem_type.value
        }

        try:
            training_stats = TrainingStats(
                data_frame, training_data_info, fairness=False)
            self.explain_stats = training_stats.get_training_statistics().get(
                "explainability_configuration")
        except Exception as e:
            raise Exception(
                "AIQES1026E", "Failed to generate statistics with error " + str(e))

        return TrainingDataStats(self.explain_stats)

    def __get_data_frame(self):
        """Get the dataframe with the training data."""
        data_frame = self.config.training_data
        data_frame = self.__validate_and_clean_data(data_frame)
        self.__convert_numeric_data_types(data_frame)
        return data_frame

    def __convert_numeric_data_types(self, data_frame):
        """Convert the data type of columns in pandas dataframe of training data if it differs from data type in payload logging configuration"""
        # Get column details from input frame
        col_names_from_df = list(data_frame.columns.values)

        for column_name in col_names_from_df:
            column_type = self.config.features_schema.get(column_name)

            if column_type and any(dtype in column_type for dtype in ("int", "double", "float", "short", "long", "decimal")) and not is_numeric_dtype(data_frame[column_name].dtype):
                data_frame[column_name] = pd.to_numeric(
                    data_frame[column_name], errors="coerce")

    def __validate_and_clean_data(self, data_frame):
        """Validate feature columns existence in training data and remove rows with invalid data"""
        features = self.config.features
        #label_column = self.config.training_data_label_col
        label_column = self.config.label_column
        # ensure that the input feature columns are present in the input training data
        if not all(elem in list(data_frame) for elem in features):
            raise Exception(
                "Either one or more of input feature columns are not present in the training data.")

        # ensure that label column is present in the input training data
        if label_column not in list(data_frame):
            raise Exception(
                "Label column is not present in the input training data")

        # if the number of rows in the input data frame is zero, throw a bad request error
        if(data_frame.shape[0] == 0):
            raise Exception("Number of rows in the input data frame is zero")

        # Select only the required subset of the dataset with features + label columns
        # Remove the rows from the dataframe that have NaN values for feature columns
        #
        # subset; indicates the list of column names to check for NaN
        # inplace; indicates to do operation inplace, meaning assign output to same variable
        try:
            req_cols = features + [label_column]
            data_frame_filtered = data_frame[req_cols].copy()
            data_frame_filtered.dropna(subset=features, inplace=True)
        except Exception as e:
            raise e

        # if the size of the rows in dataframe after removing the NaN entries from feature columns
        # equals 0, then throw an error
        if (data_frame_filtered.shape[0] == 0):
            raise Exception(
                "Number of rows in the data frame after removing NaNs is zero.")

        return data_frame_filtered


class ComputeStats():
    """Class with all the required training data details"""

    def __init__(self, stats, features, categorical_features, output_schema, problem_type):
        self.categorical_col_indexes = [
            features.index(c) for c in categorical_features]
        self.column_indexes_to_encode = self.__get_col_indexes_to_encode(
            self.categorical_col_indexes)

        data_frame = pd.DataFrame(
            np.zeros((1, len(features))), columns=features)
        self.data = data_frame[features].values
        self.output_schema = output_schema

        self.data_stats = stats.get_data_stats()
        self.class_labels = self.__get_class_labels(problem_type)

    def __get_col_indexes_to_encode(self, categorical_col_indexes):
        """Get the indexes of the categorical columns to be encoded when sending the data to lime"""
        column_indexes_to_encode = categorical_col_indexes

        return column_indexes_to_encode

    def __encode_data_and_get_encoding_map(self, stats, features, column_indexes_to_encode):
        """Encode the columns in training data based on column_indexes_to_encode and also set the categorical columns encoding map"""
        categorical_columns_encoding_mapping = {}

        if column_indexes_to_encode:
            mapping_in_stats = stats.training_data_stats.get(
                "cat_cols_encoding_map")
            for cat_col in mapping_in_stats:
                feature_type = self.output_schema.get(features[cat_col])
                if feature_type in ["boolean", "bool"]:
                    stats.training_data_stats["base_values"][cat_col] = (
                        "true" == stats.training_data_stats["base_values"][cat_col].lower())
                    categorical_columns_encoding_mapping[cat_col] = np.array(
                        [("true" == val.lower()) for val in mapping_in_stats[cat_col]])
                else:
                    categorical_columns_encoding_mapping[cat_col] = np.array(
                        mapping_in_stats[cat_col])
        return categorical_columns_encoding_mapping

    def __get_class_labels(self, problem_type):
        class_labels = []
        if problem_type != ProblemType.REGRESSION:
            labels = self.data_stats.get("class_labels")
            class_labels = [label.strip() if type(
                label) == str else label for label in labels]
        return class_labels


class TrainingDataStats():
    """
        Class to get the training data statistics
    """

    def __init__(self, training_data_stats):
        self.training_data_stats = self.__get_training_data_stats(
            training_data_stats)

    def __get_training_data_stats(self, training_data_stats: dict):
        """
            Method to get the training data statistics with keys as index
        """
        stats = {}
        for key in training_data_stats:
            key_details = training_data_stats.get(key)
            new_key_details = {}
            if(not isinstance(key_details, list)):
                for key_in_details in key_details:
                    try:
                        new_key_details[int(key_in_details)
                                        ] = key_details[key_in_details]
                    except Exception:
                        new_key_details[key_in_details
                                        ] = key_details[key_in_details]
            else:
                new_key_details = key_details
            stats[key] = new_key_details
        return stats

    def get_data_stats(self):
        """
            Method to get training stats for explainers
        """
        explainer_stats = {}
        explainer_stats["stds"] = self.training_data_stats.get("stds")
        explainer_stats["maxs"] = self.training_data_stats.get("maxs")
        explainer_stats["feature_values"] = self.training_data_stats.get(
            "feature_values")
        explainer_stats["feature_frequencies"] = self.training_data_stats.get(
            "feature_frequencies")
        explainer_stats["class_labels"] = self.training_data_stats.get(
            "class_labels")
        explainer_stats["lc_stats"] = self.training_data_stats.get("lc_stats")
        return explainer_stats
