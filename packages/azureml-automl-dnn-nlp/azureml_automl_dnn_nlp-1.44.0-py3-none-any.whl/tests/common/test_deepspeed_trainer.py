import unittest

from unittest.mock import Mock, patch

from azureml.automl.core.shared._diagnostics.automl_error_definitions import IncompatibleOrMissingDependency
from azureml.automl.core.shared.exceptions import ConfigException
from azureml.automl.dnn.nlp.common.ort_deepspeed_trainer import ORTDeepspeedTrainer


class TestOrtDsTrainer(unittest.TestCase):
    @patch("azureml.automl.dnn.nlp.common.ort_deepspeed_trainer.has_ort", True)
    @patch("azureml.automl.dnn.nlp.common.ort_deepspeed_trainer.ORTTrainer.predict")
    @patch("azureml.automl.dnn.nlp.common.ort_deepspeed_trainer.ORTTrainer.evaluate")
    def test_ortds_trainer_eval_pred(self, mock_backing_predict, mock_backing_eval):
        trainer = ORTDeepspeedTrainer(model=Mock(), args=Mock(), train_dataset=Mock())
        trainer.evaluate("some eval dataset")
        trainer.predict("some test dataset")
        mock_backing_eval.assert_called_once()
        mock_backing_predict.assert_called_once()

    @patch("azureml.automl.dnn.nlp.common.ort_deepspeed_trainer.has_ort", False)
    def test_ortds_trainer_no_optimum(self):
        with self.assertRaises(ConfigException) as exc:
            ORTDeepspeedTrainer(model=Mock(), args=Mock(), train_dataset=Mock())
        self.assertEqual(exc.exception.error_code, IncompatibleOrMissingDependency.__name__)
