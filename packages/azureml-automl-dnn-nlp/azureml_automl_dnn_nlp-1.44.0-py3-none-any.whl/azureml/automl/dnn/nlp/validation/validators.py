# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
This file contains abstract classes for dnn nlp data validation
"""
from abc import ABC, abstractmethod
from typing import Any, Optional

import logging
import pandas as pd

from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import (
    ColumnOrderingMismatch,
    ColumnSetMismatch,
    ColumnTypeMismatch,
    DuplicateColumnNames,
    InsufficientClassificationExamples,
    MissingLabelColumn
)
from azureml.automl.dnn.nlp.common.constants import ValidationLiterals, Split

_logger = logging.getLogger(__name__)


class AbstractDataValidator(ABC):
    """Common interface for all dnn nlp data validation."""

    @abstractmethod
    def validate(
            self,
            label_col_name: str,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Run validations on the user provided data inputs
        Raise error and stop the training if any validation fails

        :param label_col_name: Column name of label column.
        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate
        :return: None
        """
        raise NotImplementedError


class AbstractNLPClassificationDataValidator(AbstractDataValidator):
    """
    Common interface for dnn nlp multiclass and multilabel classification scenarios
    """
    def validate(
            self,
            label_col_name: Any,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Run validations on the user provided data inputs
        Raise error and stop the training if any validation fails

        :param label_col_name: Column name of label column.
        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate.
        :return: None
        """
        self.check_shared_validation(label_col_name, train_data, valid_data)
        self.check_custom_validation(label_col_name, train_data, valid_data)

    def check_shared_validation(
            self,
            label_col_name: Any,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Shared validation steps for multiclass and multilabel scenarios.
        Raise error and stop the training if any validation fails.
        Side effect: drops rows with null labels if found in either dataset split.

        :param label_col_name: Column name of label column.
        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate.
        :return: None
        """
        self.check_label_column(label_col_name, train_data, valid_data)
        self.check_null_labels(label_col_name, train_data, valid_data)
        self.check_feature_columns(label_col_name, train_data, valid_data)

    @abstractmethod
    def check_custom_validation(
            self,
            label_col_name: str,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        validation steps only for multiclass or multilabel scenarios
        Raise error and stop the training if any validation fails

        :param label_col_name: Column name of label column.
        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate.
        :return: None
        """
        raise NotImplementedError

    def check_feature_columns(
            self,
            label_col_name: str,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Run validation on feature columns.
        Validations included:
            check if training set or validation set have duplicated column names
            check if feature columns in training set and validation set are the same
            check if feature columns in training set and validation set have the same order
            check if columns have the same name also have the same data type
        Raise error and stop the training if any validation fails

        :param label_col_name: Column name of label column.
        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate.
        :return: None
        """
        self._check_duplicate_columns(train_data, Split.train.value)
        if valid_data is not None:
            self._check_duplicate_columns(valid_data, Split.valid.value)

        if label_col_name in train_data.columns:
            train_data = train_data.drop(columns=[label_col_name])
        if valid_data is not None:
            if label_col_name in valid_data.columns:
                valid_data = valid_data.drop(columns=[label_col_name])
        self._check_same_column_set(train_data, valid_data)
        self._check_column_order(train_data, valid_data)
        self._check_column_type(train_data, valid_data)

    def check_label_column(
            self,
            label_col_name: str,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Raise validation error if specified label column not found in either split of the data.

        :param label_col_name: Column name of label column.
        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate.
        :return: None
        """
        train_label_missing = label_col_name not in train_data.columns
        valid_label_missing = valid_data is not None and label_col_name not in valid_data.columns
        if train_label_missing or valid_label_missing:
            raise DataException._with_error(
                AzureMLError.create(
                    MissingLabelColumn,
                    col_name=label_col_name,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

    def _drop_null_and_check_size(
            self,
            label_col_name: str,
            data: pd.DataFrame,
            split_type: str,
            min_samples: int
    ) -> None:
        """
        Drop any rows with null labels IN PLACE for the given dataset.
        If this operation drops the row count to below the acceptable minimum row count, throw a validation error.

        :param label_col_name:  The name of the label column.
        :param data: The Input data
        :param split_type: which split of the data we're checking, for logging purposes
        :param min_samples: Minimum samples to check in data
        :return: None
        """
        num_samples = data.shape[0]
        data.dropna(subset=[label_col_name], inplace=True)
        non_null_num_samples = data.shape[0]

        if non_null_num_samples < num_samples:
            error_message = f"{num_samples - non_null_num_samples} samples in the {split_type} set " + \
                            "had null labels and have been dropped for training."
            _logger.info(error_message)

        if non_null_num_samples < min_samples:
            raise DataException._with_error(
                AzureMLError.create(
                    InsufficientClassificationExamples,
                    exp_cnt=min_samples,
                    act_cnt=non_null_num_samples,
                    split_type=split_type,
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

    def check_null_labels(self,
                          label_col_name: str,
                          train_data: pd.DataFrame,
                          valid_data: Optional[pd.DataFrame] = None):
        """
        Drop any rows with null labels IN PLACE for both the train and validation datasets.
        If this operation drops the row count to below the acceptable minimum row count, throw a validation error.

        :param label_col_name: The name of the label column.
        :param train_data: The training data.
        :param valid_data: The validation data, if present.
        :return: None.
        """
        self._drop_null_and_check_size(label_col_name, train_data, Split.train.value,
                                       ValidationLiterals.MIN_TRAINING_SAMPLE)
        if valid_data is not None:
            self._drop_null_and_check_size(label_col_name, valid_data, Split.valid.value,
                                           ValidationLiterals.MIN_VALIDATION_SAMPLE)

    def _check_duplicate_columns(
        self,
        data: pd.DataFrame,
        split_type: str
    ) -> None:
        """
        Check if the input data frame has columns that share the same name

        :param data: dataset passed in to check
        :param split_type: which split of the data we're checking, for logging purposes
        """
        if not len(set(data.columns)) == data.shape[1]:
            raise DataException._with_error(
                AzureMLError.create(
                    DuplicateColumnNames,
                    split_type=split_type.capitalize(),
                    target=ValidationLiterals.DATA_EXCEPTION_TARGET
                )
            )

    def _check_same_column_set(
            self,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Check if training set and validation set have the same set of columns
        Raise error and stop the training if any validation fails

        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate
        :return: None
        """
        if valid_data is not None:
            bad_cols = set(train_data.columns) ^ set(valid_data.columns)
            if bad_cols:
                raise DataException._with_error(
                    AzureMLError.create(
                        ColumnSetMismatch,
                        num_cols=len(bad_cols),
                        target=ValidationLiterals.DATA_EXCEPTION_TARGET
                    )
                )

    def _check_column_order(
            self,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Raise validation error if columns of training and validation sets have the same order.

        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate.
        :return: None
        """
        if valid_data is not None:
            for idx in range(train_data.shape[1]):
                if train_data.columns[idx] != valid_data.columns[idx]:
                    raise DataException._with_error(
                        AzureMLError.create(
                            ColumnOrderingMismatch,
                            bad_idx=idx,
                            target=ValidationLiterals.DATA_EXCEPTION_TARGET
                        )
                    )

    def _check_column_type(
            self,
            train_data: pd.DataFrame,
            valid_data: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Raise validation error if a column has different types between the training and validation sets.

        :param train_data: The training set data to validate.
        :param valid_data: The validation set data to validate.
        :return: None
        """
        if valid_data is not None:
            for idx in range(train_data.shape[1]):
                col_name = train_data.columns[idx]
                if not train_data[col_name].dtype == valid_data[col_name].dtype:
                    raise DataException._with_error(
                        AzureMLError.create(
                            ColumnTypeMismatch,
                            bad_idx=idx,
                            col_name=col_name,
                            target=ValidationLiterals.DATA_EXCEPTION_TARGET
                        )
                    )


class AbstractNERDataValidator(AbstractDataValidator):
    """Abstract validator for AutoNLP NER scenario"""

    @abstractmethod
    def validate(self, dir: str, train_file: str, valid_file: Optional[str]) -> None:
        """
        Run validations on the user provided data inputs
        Raise error and stop the training if any validation fails

        :return: None
        """
        raise NotImplementedError
