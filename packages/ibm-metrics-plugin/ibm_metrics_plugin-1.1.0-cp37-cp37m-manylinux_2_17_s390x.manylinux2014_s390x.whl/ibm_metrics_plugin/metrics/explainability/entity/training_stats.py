# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# © Copyright IBM Corp. 2021, 2022  All Rights Reserved.
# US Government Users Restricted Rights -Use, duplication or disclosure restricted by 
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import numpy as np
import pandas as pd
import collections
from collections import Counter
import numpy
from ibm_metrics_plugin.metrics.explainability.entity.bpca_impute import impute_bpca_ard, impute_transfer, impute_bpca


class TrainingStats():
    """
        Class to generate statistics related to training data. Following is the example on how the training_data_info param looks like
        :param training_data_frame: Dataframe comprising of input training data
        :type training_data_frame: DataFrame

        :param training_data_info: Input parameters needed for generating stats
        :type training_data_info:dict

        Example:
        training_data_info = {
            "label_column": "Action",
            "feature_columns": ['Gender', 'Status', 'Children', 'Age', 'Customer_Status', 'Car_Owner', 'Customer_Service', 'Satisfaction', 'Business_Area'],
            "categorical_columns": ['Gender', 'Status', 'Customer_Status', 'Car_Owner', 'Customer_Service','Business_Area'],
            "fairness_inputs": {
                "fairness_attributes": [{
                                       "feature": "Gender",
                                       "majority": ['Male'],
                                       "minority": ['Female'],
                                       "threshold": 0.6
                                   },
                                   {
                                       "feature": "Children",
                                       "majority": [[0,1]],
                                       "minority": [[2,61]],
                                       "threshold": 0.6
                                   }
                                   ],
                "min_records" : 1000,
                "favourable_class" :  [ 'Voucher' ],
                "unfavourable_class": ['Free Upgrade', 'Premium features']
            },
            "problem_type" :"multiclass"
        }

        :param explain: Flag to enable or disable stats generation for explainability
        :param explain: Boolean (True by default)

        :param fairness: Flag to enable or disable stats generation for fairness
        :param fairness: Boolean (True by default)

        :param drop_na: Flag to drop NA values from input training data
        :param drop_na: Boolean (True by default)

    """

    def __init__(self, training_data_frame, training_data_info, explain=True, fairness=True, drop_na=True):

        self.training_data_frame = training_data_frame
        self.training_data_info = training_data_info
        self.compute_explain = explain
        self.drop_na = drop_na
        self.__validate_parameters()

        if self.drop_na:
            self.__drop_na_from_data_frame()

    def __drop_na_from_data_frame(self):
        self.training_data_frame.dropna(inplace=True)
        self.training_data_frame.reset_index(drop=True, inplace=True)

    def __validate_parameters(self):
        # Valudate training data frame
        if self.training_data_frame is None:
            raise Exception("training_data_frame cannot be None or empty")

        if self.training_data_info is None or self.training_data_info == {}:
            raise Exception("Missing training_data_info")

        self.__validate_training_data_info()
        return

    def __validate_training_data_info(self):
        """
            Validate input params to training stats method
        """
        self.fairness_inputs = None
        self.feature_columns = []
        self.categorical_columns = []

        # Set problem_type(aka model_type)
        self.problem_type = self.training_data_info.get("problem_type")
        accepted_problem_types = ["regression", "binary", "multiclass"]
        if self.problem_type not in accepted_problem_types:
            raise Exception(
                "Invalid/Missing problem type. Accepted values are:" + str(accepted_problem_types))

        # Set label column (aka class_label)
        self.label_column = self.training_data_info.get("label_column")
        if self.label_column is None or len(self.label_column) == 0:
            raise Exception("'label_column' cannot be empty")

        if self.compute_explain:
            # Feature column checks
            self.feature_columns = self.training_data_info.get(
                "feature_columns")
            if self.feature_columns is None or type(self.feature_columns) is not list or len(self.feature_columns) == 0:
                raise Exception("'feature_columns should be a non empty list")

            # Verify existence of feature columns in training data
            columns_from_data_frame = list(
                self.training_data_frame.columns.values)
            check_feature_column_existence = list(
                set(self.feature_columns) - set(columns_from_data_frame))
            if len(check_feature_column_existence) > 0:
                raise Exception("Feature columns missing in training data.Details:{}".format(
                    check_feature_column_existence))

            # Verify existence of label column in training data
            if self.label_column not in columns_from_data_frame:
                raise Exception(
                    "Label column '{}' is missing in training data.".format(self.label_column))

            # Categorical column checks
            self.categorical_columns = self.training_data_info.get(
                "categorical_columns")
            if self.categorical_columns is not None and type(self.categorical_columns) is not list:
                raise Exception(
                    "'categorical_columns' should be a list of values")

            # Verify existence of  categorical columns in feature columns
            if self.categorical_columns is not None and len(self.categorical_columns) > 0:
                check_cat_col_existence = list(
                    set(self.categorical_columns) - set(self.feature_columns))
                if len(check_cat_col_existence) > 0:
                    raise Exception("'categorical_columns' should be subset of feature columns.Details:{}".format(
                        check_cat_col_existence))

    def __get_common_configuration(self):
        """
            Get common configuration details
        """
        common_configuration = {}
        common_configuration["problem_type"] = self.problem_type
        common_configuration["label_column"] = self.label_column

        try:
            input_data_schema = self.__generate_input_data_schema()
        except Exception as ex:
            raise Exception(
                "Error generating input_data_schema.Reason:%s" % ex)

        common_configuration["input_data_schema"] = input_data_schema

        if self.compute_explain:
            common_configuration["feature_fields"] = self.feature_columns
            common_configuration["categorical_fields"] = self.categorical_columns
        return common_configuration

    # Generate training schema in spark structure
    def __generate_input_data_schema(self):
        from pyspark.sql import SparkSession
        spark = SparkSession.builder.appName('pandasToSparkDF').getOrCreate()
        df = spark.createDataFrame(self.training_data_frame)
        sc = df.schema
        fields = []
        for f in sc:
            field = f.jsonValue()
            column = field["name"]

            if column in self.feature_columns:
                field["metadata"]["modeling_role"] = "feature"

                # Check for type and add to  categorical columns if not set by user
                if field["type"] == "string":
                    if self.categorical_columns is None:
                        self.categorical_columns = []

                    # Add entry to categorical column
                    if column not in self.categorical_columns and column != self.label_column:
                        self.categorical_columns.append(column)

                # Set categorical column in input schema
                if self.categorical_columns is not None:
                    if column in self.categorical_columns:
                        field["metadata"]["measure"] = "discrete"

            fields.append(field)

        training_data_schema = {}
        training_data_schema["type"] = "struct"
        training_data_schema["fields"] = fields

        return training_data_schema

    # GET the explainability configution

    def __get_explanability_configuration(self):
        from sklearn.preprocessing import LabelEncoder
        from lime.discretize import QuartileDiscretizer

        try:
            data_df = self.training_data_frame
            if self.categorical_columns is None:
                self.categorical_columns = []

            numeric_columns = list(
                set(self.feature_columns) ^ set(self.categorical_columns))

            # Convert columns to numeric incase data frame read them as non-numeric
            data_df[numeric_columns] = data_df[numeric_columns].apply(
                pd.to_numeric, errors="coerce")

            # Drop rows with invalid values
            data_df.dropna(
                axis="index", subset=self.feature_columns, inplace=True)

            random_state = 10
            training_data_schema = list(data_df.columns.values)

            # Feature column index
            feature_column_index = [training_data_schema.index(
                x) for x in self.feature_columns]

            # Categorical columns index as per feature colums
            categorical_column_index = []
            categorical_column_index = [self.feature_columns.index(
                x) for x in self.categorical_columns]

            # numeric columns
            numeric_column_index = []
            for f_col_index in feature_column_index:
                index = feature_column_index.index(f_col_index)
                if index not in categorical_column_index:
                    numeric_column_index.append(index)

            # class labels
            class_labels = []
            if self.problem_type != "regression":
                if (self.label_column != None):
                    class_labels = data_df[self.label_column].unique()
                    class_labels = class_labels.tolist()

            # Filter feature columns from training data frames
            data_frame = data_df.values
            data_frame_features = data_frame[:, feature_column_index]

            # Compute stats on complete training data
            data_frame_num_features = data_frame_features[:,
                                                          numeric_column_index]
            num_base_values = np.median(data_frame_num_features, axis=0)
            stds = np.std(data_frame_num_features, axis=0, dtype="float64")
            mins = np.min(data_frame_num_features, axis=0)
            maxs = np.max(data_frame_num_features, axis=0)

            main_base_values = {}
            main_cat_counts = {}
            if (len(categorical_column_index) > 0):
                for cat_col in categorical_column_index:
                    cat_col_value_counts = Counter(
                        data_frame_features[:, cat_col])
                    values, frequencies = map(
                        list, zip(*(cat_col_value_counts.items())))
                    max_freq_index = frequencies.index(np.max(frequencies))
                    cat_base_value = values[max_freq_index]
                    main_base_values[cat_col] = cat_base_value
                    main_cat_counts[cat_col] = cat_col_value_counts

            num_feature_range = np.arange(len(numeric_column_index))
            main_stds = {}
            main_mins = {}
            main_maxs = {}
            for x in num_feature_range:
                index = numeric_column_index[x]
                main_base_values[index] = num_base_values[x]
                main_stds[index] = stds[x]
                main_mins[index] = mins[x]
                main_maxs[index] = maxs[x]

            # Encode categorical columns
            categorical_columns_encoding_mapping = {}
            for column_index_to_encode in categorical_column_index:
                le = LabelEncoder()
                le.fit(data_frame_features[:, column_index_to_encode])
                data_frame_features[:, column_index_to_encode] = le.transform(
                    data_frame_features[:, column_index_to_encode])
                categorical_columns_encoding_mapping[column_index_to_encode] = le.classes_

            # Compute training stats on descritized data
            descritizer = QuartileDiscretizer(
                data_frame_features, categorical_features=categorical_column_index, feature_names=self.feature_columns,
                labels=class_labels, random_state=random_state)

            d_means = descritizer.means
            d_stds = descritizer.stds
            d_mins = descritizer.mins
            d_maxs = descritizer.maxs
            d_bins = descritizer.bins(data_frame_features, labels=class_labels)

            # Compute feature values and frequencies of all columns
            cat_features = np.arange(data_frame_features.shape[1])
            discretized_training_data = descritizer.discretize(
                data_frame_features)

            feature_values = {}
            feature_frequencies = {}
            for feature in cat_features:
                column = discretized_training_data[:, feature]
                feature_count = collections.Counter(column)
                values, frequencies = map(list, zip(*(feature_count.items())))
                feature_values[feature] = values
                feature_frequencies[feature] = frequencies

            index = 0
            d_bins_revised = {}
            for bin in d_bins:
                d_bins_revised[numeric_column_index[index]] = bin.tolist()
                index = index + 1

            # Encode categorical columns
            cat_col_mapping = {}
            for column_index_to_encode in categorical_column_index:
                cat_col_encoding_mapping_value = categorical_columns_encoding_mapping[
                    column_index_to_encode]
                cat_col_mapping[column_index_to_encode] = cat_col_encoding_mapping_value.tolist(
                )
        except Exception as ex:
            print(ex.with_traceback)
            raise Exception(
                "Error while generating explanability configuration.Reason:%s" % ex)

        # Construct stats
        data_stats = {}
        data_stats["feature_columns"] = self.feature_columns
        data_stats["categorical_columns"] = self.categorical_columns

        # Common
        data_stats["feature_values"] = feature_values
        data_stats["feature_frequencies"] = feature_frequencies
        data_stats["class_labels"] = class_labels
        data_stats["categorical_columns_encoding_mapping"] = cat_col_mapping

        # Descritizer
        data_stats["d_means"] = d_means
        data_stats["d_stds"] = d_stds
        data_stats["d_maxs"] = d_maxs
        data_stats["d_mins"] = d_mins
        data_stats["d_bins"] = d_bins_revised

        # Full data
        data_stats["base_values"] = main_base_values
        data_stats["stds"] = main_stds
        data_stats["mins"] = main_mins
        data_stats["maxs"] = main_maxs
        data_stats["categorical_counts"] = main_cat_counts
        data_stats["lc_stats"] = self.compute_lc_stats()

        # Convert to json
        explainability_configuration = {}
        for k in data_stats:
            key_details = data_stats.get(k)
            if (key_details is not None) and (not isinstance(key_details, list)):
                new_details = {}
                for key_in_details in key_details:
                    counter_details = key_details[key_in_details]
                    if isinstance(key_details[key_in_details], Counter):
                        counter_details = {}
                        for key, value in key_details[key_in_details].items():
                            counter_details[str(key)] = value
                    new_details[str(key_in_details)] = counter_details
            else:
                new_details = key_details
            explainability_configuration[k] = new_details

        exp_config_converted = self.__convert_numpy_int64(
            explainability_configuration)
        return exp_config_converted

    def __convert_numpy_int64(self, exp_config):
        try:
            for config in exp_config:
                config_details = exp_config.get(config)
                if isinstance(config_details, list):
                    for x in range(len(config_details)):
                        if isinstance(config_details[x], numpy.int64):
                            config_details[x] = int(config_details[x])
                elif isinstance(config_details, dict):
                    for key in config_details:
                        key_details = config_details.get(key)
                        if isinstance(key_details, list):
                            for x in range(len(key_details)):
                                if isinstance(key_details[x], numpy.int64):
                                    key_details[x] = np.asscalar(
                                        key_details[x])
                            config_details[key] = key_details
                        elif isinstance(key_details, numpy.int64):
                            config_details[key] = int(key_details)
                exp_config[config] = config_details
        except Exception as ex:
            raise Exception("Error while coverting numpy int64.Reason:%s" % ex)
        return exp_config

    def get_training_statistics(self):
        """
            Method to generate training data distribution
        """
        stats_configuration = {}

        common_config = self.__get_common_configuration()
        stats_configuration["common_configuration"] = common_config

        if self.compute_explain:
            explain_config = self.__get_explanability_configuration()
            stats_configuration["explainability_configuration"] = explain_config

        return stats_configuration

    def __fill_missing_values_in_data_frame_lc(self):
        np_array = self.training_data_frame.to_numpy().T
        filled_array, _ = impute_bpca(np_array)
        self.training_data_frame = pd.DataFrame(
            filled_array, columns=self.training_data_frame.columns)

    def __get_transfer_params_training_data(self):
        _, param = impute_bpca_ard(self.training_data_frame.to_numpy().T)
        return param["W"], param["mu"]

    def compute_lc_stats(self):
        lc_stats = {}
        x_train = self.training_data_frame.to_numpy().T
        lc_stats["mean"] = np.nanmean(x_train, axis=1).reshape(-1, 1)
        lc_stats["std"] = np.nanstd(x_train, axis=1).reshape(-1, 1)
        lc_stats["w"], lc_stats["mu"] = self.__get_transfer_params_training_data()
        return lc_stats
