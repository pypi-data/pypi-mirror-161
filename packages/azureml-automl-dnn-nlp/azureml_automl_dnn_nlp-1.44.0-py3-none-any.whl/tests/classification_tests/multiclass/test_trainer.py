from unittest.mock import MagicMock, PropertyMock, patch

import numpy as np
import os
import pandas as pd
import pytest
import sys

from azureml.automl.dnn.nlp.classification.common.constants import MultiClassParameters
from azureml.automl.dnn.nlp.common._resource_path_resolver import ResourcePathResolver
from azureml.automl.dnn.nlp.classification.io.read.dataloader import load_and_validate_multiclass_dataset
from azureml.automl.dnn.nlp.classification.multiclass.trainer import TextClassificationTrainer
from azureml.automl.dnn.nlp.common.constants import SystemSettings
from ...mocks import multiclass_trainer_mock, aml_dataset_mock


@pytest.mark.usefixtures('MulticlassDatasetTester')
@pytest.mark.usefixtures('MulticlassValDatasetTester')
@pytest.mark.usefixtures('MulticlassTokenizer')
@pytest.mark.parametrize('multiple_text_column', [True, False])
@pytest.mark.parametrize('include_label_col', [True])
@pytest.mark.parametrize('enable_distributed', [True, False])
@pytest.mark.parametrize('is_long_range_text', [True, False])
@pytest.mark.parametrize('enable_long_range_text', [True, False])
class TestTextClassificationTrainerTests:
    """Tests for Text Classification trainer."""
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoConfig")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.classification.multiclass.trainer.DistributedTrainer")
    @patch("azureml.core.Dataset.get_by_id")
    @patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver.tokenizer",
           new_callable=PropertyMock)
    @patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver.model_name",
           new_callable=PropertyMock)
    @patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver.model_path",
           new_callable=PropertyMock)
    def test_train_valid(self, model_path_mock, model_name_mock, tokenizer_mock, get_by_id_mock,
                         distributed_trainer_mock, trainer_mock, auto_config_mock, auto_model_mock,
                         MulticlassDatasetTester, MulticlassValDatasetTester, enable_distributed,
                         MulticlassTokenizer, is_long_range_text, enable_long_range_text):
        train_df = MulticlassDatasetTester.get_data(is_long_range_text).copy()
        validation_df = MulticlassValDatasetTester.get_data(is_long_range_text).copy()
        label_column_name = "labels_col"
        concat_df = pd.concat([train_df, validation_df], ignore_index=True)
        mock_aml_dataset = aml_dataset_mock(concat_df)
        get_by_id_mock.return_value = mock_aml_dataset
        aml_workspace_mock = MagicMock()
        automl_settings = dict()
        automl_settings['dataset_id'] = 'mock_id'
        automl_settings['validation_dataset_id'] = 'mock_validation_id'
        training_set, validation_set, label_list, _, _, _ = load_and_validate_multiclass_dataset(
            aml_workspace_mock, "data_dir", label_column_name,
            MulticlassTokenizer, automl_settings, enable_long_range_text=enable_long_range_text
        )

        auto_config_mock.from_pretrained.return_value = MagicMock()
        auto_model_mock.from_pretrained.return_value = MagicMock()
        tokenizer_mock.return_value = MagicMock()
        model_name_mock.return_value = "some model"
        model_path_mock.return_value = "some path"
        rpr = ResourcePathResolver("eng", False)
        tokenizer = rpr.tokenizer
        tokenizer.name_or_path = "some path"
        tokenizer_mock.assert_called_once()
        tokenizer_mock.reset_mock()

        trainer_multiclass = TextClassificationTrainer(label_list, rpr, enable_distributed=enable_distributed,
                                                       tokenizer=tokenizer)

        # trainer mock
        mock_trainer = multiclass_trainer_mock(len(concat_df))
        distributed_mock_trainer = multiclass_trainer_mock(len(concat_df))
        trainer_mock.return_value = mock_trainer
        distributed_trainer_mock.return_value = distributed_mock_trainer

        trainer_multiclass.train(training_set)
        if enable_long_range_text and is_long_range_text:
            assert training_set.max_seq_length == MultiClassParameters.MAX_SEQ_LENGTH_256
            assert trainer_multiclass.training_args.gradient_accumulation_steps == 2
            assert trainer_multiclass.training_args.per_device_train_batch_size == 16
        else:
            assert training_set.max_seq_length == MultiClassParameters.MAX_SEQ_LENGTH_128
            assert trainer_multiclass.training_args.gradient_accumulation_steps == 1
            assert trainer_multiclass.training_args.per_device_train_batch_size == 32

        # train function
        trainer_multiclass.trainer.train.assert_called_once()
        trainer_multiclass.trainer.save_model.assert_called_once()
        trainer_multiclass.trainer.save_state.assert_called_once()

        # validate function
        predictions = trainer_multiclass.validate(validation_set)
        trainer_multiclass.trainer.predict.assert_called_once()
        assert predictions.shape == (len(concat_df), len(label_list))
        trainer_multiclass.trainer.save_metrics.assert_called_once()
        tokenizer_mock.assert_not_called()
        model_name_mock.assert_called_once()
        model_path_mock.assert_called_once()
        assert auto_config_mock.from_pretrained.call_args[0][0] == "some path"
        assert auto_model_mock.from_pretrained.call_args[0][0] == "some path"
        if enable_distributed is True:
            assert trainer_multiclass.trainer is distributed_mock_trainer


@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.np.save')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.os.path.exists')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.ORTDeepspeedTrainer')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoConfig.from_pretrained')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.AutoModelForSequenceClassification.from_pretrained')
@patch('azureml.automl.dnn.nlp.classification.multiclass.trainer.ResourcePathResolver.tokenizer',
       new_callable=PropertyMock)
@patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver.model_name",
       new_callable=PropertyMock)
@patch("azureml.automl.dnn.nlp.common._resource_path_resolver.ResourcePathResolver.model_path",
       new_callable=PropertyMock)
def test_ort_trainer(model_path_mock, model_name_mock, tokenizer_mock,
                     model_factory_mock, config_factory_mock,
                     ort_trainer_mock, mock_path_check, mock_np_save):
    tokenizer_mock.return_value = MagicMock(name_or_path="some_path")
    trainer = TextClassificationTrainer(train_label_list=np.arange(5),
                                        resource_path_resolver=ResourcePathResolver("eng", False),
                                        enable_distributed_ort_ds=True)
    mock_path_check.side_effect = [False, True, True, True]
    dataset = MagicMock(max_seq_length=128)
    # ORT trainer without deepspeed enabled
    with patch.dict(sys.modules, {"deepspeed": MagicMock()}):
        trainer.train(dataset)
    assert ort_trainer_mock.call_count == 1
    assert ort_trainer_mock.call_args[1]['args'].deepspeed is None
    assert ort_trainer_mock.call_args[1]['args'].fp16 is False
    assert ort_trainer_mock.return_value.save_metrics.call_count == 1

    # ORT trainer with deepspeed enabled
    with patch.dict(sys.modules, {"deepspeed": MagicMock(__spec__=MagicMock())}):  # deepspeed importable
        with patch.dict(os.environ, {"LOCAL_RANK": "0"}):  # distributed env var present
            with patch('torch.cuda.set_device'):  # setting cuda device doesn't complain
                trainer.train(dataset)
    assert ort_trainer_mock.call_count == 2
    assert ort_trainer_mock.call_args[1]['args'].deepspeed == SystemSettings.DEEP_SPEED_CONFIG
    assert ort_trainer_mock.call_args[1]['args'].fp16 is True
    assert ort_trainer_mock.return_value.save_metrics.call_count == 2
