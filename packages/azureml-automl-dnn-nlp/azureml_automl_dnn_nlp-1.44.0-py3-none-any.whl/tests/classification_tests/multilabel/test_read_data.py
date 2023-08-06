from unittest.mock import MagicMock, Mock, patch, PropertyMock

import ast
import json
import numpy as np
import os
import pandas as pd
import pytest
import unittest

from azureml.automl.core.shared.exceptions import DataException
from azureml.automl.dnn.nlp.classification.io.read.pytorch_dataset_wrapper import PyTorchDatasetWrapper
from azureml.automl.dnn.nlp.classification.io.read.dataloader import load_and_validate_multilabel_dataset
from azureml.automl.dnn.nlp.classification.io.read.read_utils import get_y_transformer
from azureml.automl.dnn.nlp.common._diagnostics.nlp_error_definitions import MissingDataset
from azureml.automl.dnn.nlp.common.constants import DataLiterals, Split
from ...mocks import aml_dataset_mock, aml_label_dataset_mock, get_multilabel_labeling_df, open_classification_file

try:
    import torch
    has_torch = True
except ImportError:
    has_torch = False


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [False])
class TestPyTorchDatasetWrapper:
    @unittest.skipIf(not has_torch, "torch not installed")
    def test_pytorch_dataset_wrapper(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        dataset_language = "some_language"
        label_column_name = "labels_col"
        y_transformer = get_y_transformer(input_df, input_df, label_column_name)
        num_label_cols = len(y_transformer.classes_)
        assert num_label_cols == 6
        training_set = PyTorchDatasetWrapper(input_df, dataset_language,
                                             label_column_name=label_column_name, y_transformer=y_transformer)
        assert len(training_set) == 50
        assert set(training_set[1].keys()) == {'ids', 'mask', 'token_type_ids', 'targets'}
        assert all(torch.is_tensor(value) for key, value in training_set[1].items())
        downloaded_path = os.path.join(training_set.tokenizer.name_or_path, 'tokenizer_config.json')
        with open(downloaded_path, "r") as read_file:
            obj = json.load(read_file)
        assert obj['name_or_path'] == 'bert-base-multilingual-cased'

        expected_targets = y_transformer.transform([ast.literal_eval(input_df["labels_col"][1])])
        expected_targets = expected_targets.toarray().astype(int)[0]
        actual_targets = training_set[1]['targets'].detach().numpy()
        assert np.array_equal(actual_targets, expected_targets)
        assert np.issubdtype(actual_targets.dtype, np.integer) and np.issubdtype(expected_targets.dtype, np.integer)

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_pytorch_dataset_wrapper_for_inference(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        input_df = input_df.drop(columns=["labels_col"]).reset_index(drop=True)
        dataset_language = "some_language"
        training_set = PyTorchDatasetWrapper(input_df, dataset_language)
        assert len(training_set) == 50
        assert set(training_set[1].keys()) == {'ids', 'mask', 'token_type_ids'}
        assert all(torch.is_tensor(value) for key, value in training_set[1].items())

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        dataset_language = "some_language"
        label_column_name = "labels_col"
        y_transformer = get_y_transformer(input_df, input_df, label_column_name)
        num_label_cols = len(y_transformer.classes_)
        assert num_label_cols == 6
        with patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver.tokenizer",
                   new_callable=PropertyMock) as mock_get_tokenizer:
            tokenizer_mock = Mock()
            # We don't really care about this input; just set something that won't error.
            tokenizer_mock.encode_plus.return_value = {"input_ids": np.array([1, 2, 3]),
                                                       "attention_mask": np.array([1, 2, 3]),
                                                       "token_type_ids": np.array([1, 2, 3])}
            mock_get_tokenizer.return_value = tokenizer_mock
            training_set = PyTorchDatasetWrapper(input_df, dataset_language,
                                                 label_column_name=label_column_name, y_transformer=y_transformer)
        _ = training_set[0]  # noqa: F841
        assert tokenizer_mock.encode_plus.call_args[0][0] == \
            "This is a small sample dataset containing cleaned text data."

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation_inference(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        input_df = input_df.drop(columns=["labels_col"]).reset_index(drop=True)
        dataset_language = "some_language"
        with patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver.tokenizer",
                   new_callable=PropertyMock) as mock_get_tokenizer:
            tokenizer_mock = Mock()
            # We don't really care about this input; just set something that won't error.
            tokenizer_mock.encode_plus.return_value = {"input_ids": np.array([1, 2, 3]),
                                                       "attention_mask": np.array([1, 2, 3]),
                                                       "token_type_ids": np.array([1, 2, 3])}
            mock_get_tokenizer.return_value = tokenizer_mock
            training_set = PyTorchDatasetWrapper(input_df, dataset_language)
        _ = training_set[0]  # noqa: F841
        assert tokenizer_mock.encode_plus.call_args[0][0] == \
            "This is a small sample dataset containing cleaned text data."

    def test_get_y_transformer(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        # Test both cases, with and without validation data
        for valid_df in [input_df, None]:
            y_transformer = get_y_transformer(input_df, valid_df, label_column_name)
            num_label_cols = len(y_transformer.classes_)
            assert num_label_cols == 6
            assert set(y_transformer.classes_) == {'A', 'a', '1', '2', 'label5', 'label6'}

    @unittest.skipIf(not has_torch, "torch not installed")
    @patch("azureml.core.Dataset.get_by_id")
    def test_load_multilabel_dataset(self, get_by_id_mock, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset
        automl_settings = dict()
        automl_settings['dataset_id'] = 'mock_id'
        automl_settings['validation_dataset_id'] = 'mock_validation_id'
        aml_workspace_mock = MagicMock()
        dataset_language = "some_language"
        training_set, validation_set, num_label_cols, _ = load_and_validate_multilabel_dataset(
            aml_workspace_mock, DataLiterals.DATA_DIR, label_column_name, automl_settings, None, dataset_language)
        assert num_label_cols == 6
        for output_set in [training_set, validation_set]:
            assert type(output_set) == PyTorchDatasetWrapper
            assert len(output_set) == 50
            assert all(set(output_set[i].keys())
                       == {'ids', 'mask', 'token_type_ids', 'targets'} for i in range(len(output_set)))

    @unittest.skipIf(not has_torch, "torch not installed")
    @pytest.mark.parametrize(
        'mltable_data_json', [
            None,
            '{"TrainData": {"Uri": "azuremluri", "ResolvedUri": "resolved_uri"}, '
            '"ValidData": null}'
        ]
    )
    @patch("azureml.data.abstract_dataset.AbstractDataset._load")
    @patch("azureml.core.Dataset.get_by_id")
    def test_load_multilabel_dataset_no_val_set(self, get_by_id_mock, dataset_load_mock,
                                                mltable_data_json, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        mock_aml_dataset = aml_dataset_mock(input_df)
        get_by_id_mock.return_value = mock_aml_dataset
        dataset_load_mock.return_value = mock_aml_dataset
        automl_settings = dict()
        if mltable_data_json is None:
            automl_settings['dataset_id'] = 'mock_id'
        aml_workspace_mock = MagicMock()
        dataset_language = "some_language"

        with pytest.raises(DataException) as exc:
            load_and_validate_multilabel_dataset(
                aml_workspace_mock, DataLiterals.DATA_DIR, label_column_name, automl_settings,
                mltable_data_json=mltable_data_json, dataset_language=dataset_language)
        assert exc.value.error_code == MissingDataset.__name__
        assert Split.valid.value.capitalize() in exc.value.message_format

    @unittest.skipIf(not has_torch, "torch not installed")
    @patch("azureml.core.Dataset.get_by_id")
    def test_load_multilabel_dataset_labeling_service(self, get_by_id_mock):
        label_column_name = "label"
        mock_aml_dataset = aml_label_dataset_mock('TextClassificationMultiLabel', get_multilabel_labeling_df())
        get_by_id_mock.return_value = mock_aml_dataset
        automl_settings = dict()
        automl_settings['dataset_id'] = 'mock_id'
        automl_settings['validation_dataset_id'] = 'mock_validation_id'
        aml_workspace_mock = MagicMock()
        with patch("azureml.automl.dnn.nlp.classification.io.read._labeling_data_helper.open",
                   new=open_classification_file):
            training_set, validation_set, num_label_cols, _ = load_and_validate_multilabel_dataset(
                aml_workspace_mock, DataLiterals.DATA_DIR, label_column_name, automl_settings, None,
                is_labeling_run=True,
            )
        assert num_label_cols == 2
        for output_set in [training_set, validation_set]:
            assert type(output_set) == PyTorchDatasetWrapper
            assert len(output_set) == 60
            assert all(set(output_set[i].keys())
                       == {'ids', 'mask', 'token_type_ids', 'targets'} for i in range(len(output_set)))

    @unittest.skipIf(not has_torch, "torch not installed")
    @patch("azureml.data.abstract_dataset.AbstractDataset._load")
    def test_load_multilabel_dataset_mlflow_data_json(self, dataset_load_mock, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        mock_aml_dataset = aml_dataset_mock(input_df)
        dataset_load_mock.return_value = mock_aml_dataset
        automl_settings = dict()
        mltable_data_json = '{"TrainData": {"Uri": "azuremluri", "ResolvedUri": "resolved_uri"}, ' \
                            '"ValidData": {"Uri": "azuremluri2", "ResolvedUri": "resolved_uri2"}}'
        aml_workspace_mock = MagicMock()
        dataset_language = "some_language"
        training_set, validation_set, num_label_cols, _ = load_and_validate_multilabel_dataset(
            aml_workspace_mock, DataLiterals.DATA_DIR, label_column_name, automl_settings,
            mltable_data_json, dataset_language
        )
        assert num_label_cols == 6
        for output_set in [training_set, validation_set]:
            assert type(output_set) == PyTorchDatasetWrapper
            assert len(output_set) == 50
            assert all(set(output_set[i].keys())
                       == {'ids', 'mask', 'token_type_ids', 'targets'} for i in range(len(output_set)))

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_multilabel_wrapped_dataset_non_standard_indexed_dataframes(self):
        train_data = pd.DataFrame({"input_text_col": np.array(["I should eat some lunch.",
                                                               "Do I order out?",
                                                               "Or do I make something here?",
                                                               "Oh the many decisions faced by the average person."]),
                                   "labels": np.array(["['yes']", "['no']", "['yes']", "['tragic']"])})
        train_data.index = np.array([0, 1, 3, 4])
        y_transformer = get_y_transformer(train_data, None, "labels")
        wrapped_train = PyTorchDatasetWrapper(train_data, "eng", "labels", y_transformer)
        assert torch.equal(wrapped_train[2]["targets"], torch.tensor(np.array([0, 0, 1]), dtype=torch.long))


@pytest.mark.usefixtures('MultilabelDatasetTester')
@pytest.mark.parametrize('multiple_text_column', [True])
class TestPyTorchDatasetWrapperMultipleColumns:
    @unittest.skipIf(not has_torch, "torch not installed")
    def test_pytorch_dataset_wrapper(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        dataset_language = "some_language"
        y_transformer = get_y_transformer(input_df, input_df, label_column_name)
        num_label_cols = len(y_transformer.classes_)
        assert num_label_cols == 6
        training_set = PyTorchDatasetWrapper(input_df, dataset_language,
                                             label_column_name=label_column_name, y_transformer=y_transformer)
        assert len(training_set) == 50
        assert all(item in ['ids', 'mask', 'token_type_ids', 'targets'] for item in training_set[1])
        assert all(torch.is_tensor(value) for key, value in training_set[1].items())

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        dataset_language = "some_language"
        y_transformer = get_y_transformer(input_df, input_df, label_column_name)
        num_label_cols = len(y_transformer.classes_)
        assert num_label_cols == 6
        with patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver.tokenizer",
                   new_callable=PropertyMock) as mock_get_tokenizer:
            tokenizer_mock = Mock()
            # We don't really care about this input; just set something that won't error.
            tokenizer_mock.encode_plus.return_value = {"input_ids": np.array([1, 2, 3]),
                                                       "attention_mask": np.array([1, 2, 3]),
                                                       "token_type_ids": np.array([1, 2, 3])}
            mock_get_tokenizer.return_value = tokenizer_mock
            training_set = PyTorchDatasetWrapper(input_df, dataset_language,
                                                 label_column_name=label_column_name, y_transformer=y_transformer)
        expected = 'This is a small sample dataset containing cleaned text data.. This is an additional column.'
        _ = training_set[0]  # noqa: F841
        assert tokenizer_mock.encode_plus.call_args[0][0] == expected

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_get_y_transformer(self, MultilabelDatasetTester):
        input_df = MultilabelDatasetTester.get_data().copy()
        label_column_name = "labels_col"
        # Test both cases, with and without validation data
        for valid_df in [input_df, None]:
            y_transformer = get_y_transformer(input_df, valid_df, label_column_name)
            num_label_cols = len(y_transformer.classes_)
            assert num_label_cols == 6
            assert set(y_transformer.classes_) == {'A', 'a', '1', '2', 'label5', 'label6'}

    @unittest.skipIf(not has_torch, "torch not installed")
    def test_column_concatenation_with_null_col_vals(self):
        input_df = pd.DataFrame({
            "column1": np.array(["This is a sentence", "Is this a question?", "Exclamatory remark, wow!",
                                 "a sentence fragment", None]),
            "column2": np.array(["This is a second sentence", "Is this a second question?",
                                 "Second exclamatory remark, double wow!", "second sentence fragment", "Word."]),
            "label": np.array(["['sentence']", "['question']", "['exclamatory', 'sentence']",
                               "['fragment']", "['fragment']"])
        })
        input_df = pd.concat((input_df for _ in range(10)), axis=0, ignore_index=True)
        y_transformer = get_y_transformer(input_df, None, "label")

        with patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver.tokenizer",
                   new_callable=PropertyMock) as mock_get_tokenizer:
            tokenizer_mock = Mock()
            # We don't really care about this input; just set something that won't error.
            tokenizer_mock.encode_plus.return_value = {"input_ids": np.array([1, 2, 3]),
                                                       "attention_mask": np.array([1, 2, 3]),
                                                       "token_type_ids": np.array([1, 2, 3])}
            mock_get_tokenizer.return_value = tokenizer_mock
            wrapped_train = PyTorchDatasetWrapper(input_df, dataset_language="eng",
                                                  label_column_name="label", y_transformer=y_transformer)
            # trigger __getitem__, which concatenates text
            _ = wrapped_train[0]  # noqa: F841
            assert tokenizer_mock.encode_plus.call_args[0][0] == "This is a sentence. This is a second sentence"

            # trigger concatenation with none value
            _ = wrapped_train[4]  # noqa: F841
            assert tokenizer_mock.encode_plus.call_args[0][0] == "None. Word."


@pytest.mark.usefixtures("MultilabelNoisyLabelsTester")
class TestMultilabelLabelParser:
    @pytest.mark.parametrize("special_token", ['.', '-', '_', '+', ''])
    def test_noise_label(self, special_token, MultilabelNoisyLabelsTester):
        input_df = MultilabelNoisyLabelsTester.get_data().copy()
        y_transformer = get_y_transformer(input_df, None, "labels")
        print(y_transformer.classes_)
        assert len(y_transformer.classes_) == 5
        expected = ['1', '2', f'A{special_token}B', f'C{special_token}D', f'E{special_token}F']
        assert set(y_transformer.classes_) == set(expected)
