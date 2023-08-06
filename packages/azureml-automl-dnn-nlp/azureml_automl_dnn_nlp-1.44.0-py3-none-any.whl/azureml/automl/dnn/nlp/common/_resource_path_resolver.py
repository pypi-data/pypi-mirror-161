# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""path resolver for config, tokenizer and model given dataset language and is_multilabel."""
import logging
import os

from transformers import AutoTokenizer, PreTrainedTokenizerBase

from azureml.automl.core._downloader import Downloader
from azureml.automl.core.shared import constants, logging_utilities as log_utils
from azureml.automl.dnn.nlp.common._utils import get_unique_download_path
from azureml.automl.dnn.nlp.common.constants import ModelNames
from azureml.automl.runtime.featurizer.transformer.data.automl_textdnn_provider import AutoMLPretrainedDNNProvider
from azureml.automl.runtime.featurizer.transformer.data.word_embeddings_info import EmbeddingInfo


BASE_URL = "https://aka.ms/automl-resources/nlp-pretrained/"
TOKENIZER_ZIP = 'tokenizer.zip'
ZIP_FILE_PREFIX = 'azureml_automl_nlp'
_logger = logging.getLogger(__name__)


class ResourcePathResolver:
    """Class to resolve the paths for config, tokenizer and model"""

    def __init__(
            self,
            dataset_language: str,
            is_multilabel_training: bool
    ):
        """Function to initialize the ResourcePathResolver object

        :param dataset_language: user-inputted language from FeaturizationConfig
        :param is_multilabel_training: training type

        """
        self.dataset_language = dataset_language
        self.is_multilabel_training = is_multilabel_training
        self._lower_case = True
        if dataset_language.lower() == 'eng':
            if is_multilabel_training:
                self._model_name = ModelNames.BERT_BASE_UNCASED
                self._embedded_model_name = EmbeddingInfo.BERT_BASE_UNCASED_AUTONLP_3_1_0
                self._lower_case = False
            else:
                self._model_name = ModelNames.BERT_BASE_CASED
                self._embedded_model_name = EmbeddingInfo.BERT_BASE_CASED
        elif dataset_language.lower() == 'deu':
            self._model_name = ModelNames.BERT_BASE_GERMAN_CASED
            self._embedded_model_name = EmbeddingInfo.BERT_BASE_GERMAN_CASED_AUTONLP_3_1_0
        else:
            self._model_name = ModelNames.BERT_BASE_MULTILINGUAL_CASED
            self._embedded_model_name = EmbeddingInfo.BERT_BASE_MULTLINGUAL_CASED_AUTONLP_3_1_0
        self._model_path = None  # type: str
        self._tokenizer_path = None  # type: str
        self._config_path = None  # type: str

    @property
    def model_name(self) -> str:
        """
        Property returns model to use
        :return model name
        """
        return self._model_name

    @property
    def config_path(self) -> str:
        """
        Property returns config path
        :return config path
        """
        # config is zipped in same folder along with tokenizer and is required to load tokenizer.
        if self._tokenizer_path is None:
            self._download_tokenizer_and_config()
        return self._tokenizer_path

    @property
    def model_path(self) -> str:
        """
        Property returns model path
        :return model path
        """
        if self._model_path is None:
            self._download_model()
        if self._model_path is None:
            _logger.warning(f"Failed to Download {self.model_name} from CDN")
        else:
            _logger.info(f"Downloaded {self.model_name} to '{self._model_path}'")
        return self._model_path

    @property
    def tokenizer_path(self) -> str:
        """
        Property returns tokenizer path  that has the tokenizer downloded from CDN
        :return tokenizer path
        """
        if self._tokenizer_path is None:
            self._download_tokenizer_and_config()
        return self._tokenizer_path

    @property
    def tokenizer(self) -> PreTrainedTokenizerBase:
        """
        Property returns a tokenizer from tokenizer path or  using HF.
        :return: PreTrainedTokenizerBase
        """
        model_name_or_path = self.tokenizer_path if self.tokenizer_path else self.model_name
        return AutoTokenizer.from_pretrained(model_name_or_path, use_fast=True)

    def _download_model(self):
        """Download the model"""
        provider = AutoMLPretrainedDNNProvider(self._embedded_model_name)
        self._model_path = provider.get_model_dirname()

    def _download_tokenizer_and_config(self):
        """Download the zip file with tokenizer and unzip it"""

        download_type = constants.TelemetryConstants.EXTERNAL_DOWNLOAD
        download_prefix = BASE_URL + self._model_name + "/"
        download_type = constants.TelemetryConstants.CDN_DOWNLOAD
        with log_utils.log_activity(
                _logger,
                activity_name=f"{download_type}_{self._model_name}"
        ):
            local_path = get_unique_download_path('tokenizer')
            pid = str(os.getpid())
            download_path = os.path.join(os.path.realpath(os.path.curdir), 'pid', pid, local_path)
            if not os.path.isdir(download_path):
                os.makedirs(download_path)
            try:
                downloaded_file = Downloader.download(download_prefix=download_prefix,
                                                      file_name=TOKENIZER_ZIP,
                                                      target_dir=download_path,
                                                      prefix=ZIP_FILE_PREFIX)

                if os.path.exists(downloaded_file):
                    Downloader.unzip_file(zip_fname=downloaded_file, extract_path=download_path)
                    _logger.info(f"Downloaded tokenizer for {self._model_name}"
                                 f"from CDN {download_prefix}/{TOKENIZER_ZIP}")
                    self._tokenizer_path = download_path
                    self._config_path = download_path
                else:
                    _logger.warning(f"Missing tokenizer downloaded file '{downloaded_file}'")
            except Exception as e:
                _logger.warning(f"Download for tokenizer failed with error: {e}")
