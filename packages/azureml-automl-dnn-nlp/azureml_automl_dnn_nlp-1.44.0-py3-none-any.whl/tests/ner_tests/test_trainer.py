from unittest.mock import MagicMock, patch

import os
import pytest
import numpy as np
import sys
import unittest

from azureml.automl.core.shared.constants import Metric
from azureml.automl.core.shared.exceptions import ValidationException
from azureml.automl.dnn.nlp.common.constants import OutputLiterals, SystemSettings
from azureml.automl.dnn.nlp.ner.trainer import NERPytorchTrainer

from ..mocks import ner_trainer_mock


@pytest.mark.usefixtures('new_clean_dir')
class NERTrainerTests(unittest.TestCase):
    """Tests for NER trainer."""

    @patch("azureml.automl.dnn.nlp.ner.trainer.Trainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    def test_train_valid(
            self,
            model_mock,
            trainer_mock
    ):
        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # trainer mock
        mock_trainer = ner_trainer_mock()
        trainer_mock.return_value = mock_trainer

        # prepare input params for trainer
        train_dataset = MagicMock()
        eval_dataset = MagicMock()
        label_list = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
        model_name, download_dir = "bert-base-cased", "some_path"
        output_dir = OutputLiterals.OUTPUT_DIR
        trainer = NERPytorchTrainer(
            label_list,
            model_name,
            download_dir,
            output_dir
        )

        # train
        assert model_mock.from_pretrained.call_args[0][0] == "some_path"
        trainer.train(train_dataset)
        trainer.trainer.train.assert_called_once()
        trainer.trainer.save_model.assert_called_once()
        trainer.trainer.save_state.assert_called_once()

        # valid
        results = trainer.validate(eval_dataset)
        trainer.trainer.evaluate.assert_called_once()
        assert results is not None
        for primary_metric in Metric.TEXT_NER_PRIMARY_SET:
            assert primary_metric in results

    @patch("azureml.automl.dnn.nlp.ner.trainer.DistributedTrainer")
    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    def test_distributed_trainer(
            self,
            model_mock,
            distributed_trainer_mock
    ):
        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # trainer mock
        mock_trainer = ner_trainer_mock()
        distributed_trainer_mock.return_value = mock_trainer

        # prepare input params for trainer
        train_dataset = MagicMock()
        label_list = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
        model_name, download_dir = "bert-base-cased", "some_path"
        output_dir = OutputLiterals.OUTPUT_DIR
        trainer = NERPytorchTrainer(
            label_list,
            model_name,
            download_dir,
            output_dir,
            enable_distributed=True
        )

        trainer.train(train_dataset)
        mock_trainer.train.assert_called_once

    @patch("azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification")
    def test_validation_without_train(
            self,
            model_mock
    ):
        # model mock
        model = MagicMock()
        model.from_pretrained.return_value = MagicMock()
        model_mock.return_value = model

        # prepare input params
        eval_dataset = MagicMock()
        label_list = ["O", "B-MISC", "I-MISC", "B-PER", "I-PER", "B-ORG", "I-ORG", "B-LOC", "I-LOC"]
        model_name, download_dir = "bert-base-cased", "some-download-dir"
        output_dir = OutputLiterals.OUTPUT_DIR
        trainer = NERPytorchTrainer(
            label_list,
            model_name,
            download_dir,
            output_dir
        )

        with self.assertRaises(ValidationException):
            trainer.validate(eval_dataset)

        assert trainer.trainer is None

    @patch('azureml.automl.dnn.nlp.ner.trainer.os.path.exists')
    @patch('azureml.automl.dnn.nlp.ner.trainer.ORTDeepspeedTrainer')
    @patch('azureml.automl.dnn.nlp.ner.trainer.AutoConfig.from_pretrained')
    @patch('azureml.automl.dnn.nlp.ner.trainer.AutoModelForTokenClassification.from_pretrained')
    def test_ort_trainer(self,
                         model_factory_mock,
                         config_factory_mock,
                         ort_trainer_mock,
                         mock_path_check):
        trainer = NERPytorchTrainer(label_list=np.array(["O", "B-MISC", "I-MISC", "B-PER", "I-PER"]),
                                    model_name="some-model", download_dir="some-dir",
                                    output_dir="output-dir", enable_distributed_ort_ds=True)
        mock_path_check.side_effect = [False, True]
        # ORT trainer without deepspeed enabled
        with patch.dict(sys.modules, {"deepspeed": MagicMock()}):
            trainer.train(MagicMock())
        assert ort_trainer_mock.call_count == 1
        assert ort_trainer_mock.call_args[1]['args'].deepspeed is None
        assert ort_trainer_mock.call_args[1]['args'].fp16 is False

        # ORT trainer with deepspeed enabled
        with patch.dict(sys.modules, {"deepspeed": MagicMock(__spec__=MagicMock())}):  # deepspeed importable
            with patch.dict(os.environ, {"LOCAL_RANK": "0"}):  # distributed env var present
                with patch('torch.cuda.set_device'):  # setting cuda device doesn't complain
                    trainer.train(MagicMock())
        assert ort_trainer_mock.call_count == 2
        assert ort_trainer_mock.call_args[1]['args'].deepspeed == SystemSettings.DEEP_SPEED_CONFIG
        assert ort_trainer_mock.call_args[1]['args'].fp16 is True
