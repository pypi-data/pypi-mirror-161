# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Test for pretrained model utilities for the package."""

from collections import OrderedDict
from unittest.mock import patch, call

import pytest

from azureml.automl.dnn.vision.common.constants import PretrainedSettings
from azureml.automl.dnn.vision.common.pretrained_model_utilities import PretrainedModelFactory


class TestPretrainedModelFactory:
    """The Factory class of creating the pretrained models that are used by the package."""

    @patch("azureml.automl.dnn.vision.common.pretrained_model_utilities.load_state_dict_from_url")
    def test_load_state_dict_from_url_with_retry_with_no_exception(self, mock_load_state_dict_from_url):
        mock_load_state_dict_from_url.return_value = OrderedDict()
        return_value = PretrainedModelFactory._load_state_dict_from_url_with_retry(url="https://aka.ms"
                                                                                       "/dummy_model.pth")
        assert type(return_value) == OrderedDict
        mock_load_state_dict_from_url.assert_called_once()

    @patch("random.uniform", return_value=0.5)
    @patch("time.sleep", return_value=None)
    @patch("azureml.automl.dnn.vision.common.pretrained_model_utilities.load_state_dict_from_url")
    def test_load_state_dict_from_url_with_retry_with_exceptions(self, mock_load_state_dict_from_url, mock_sleep,
                                                                 mock_random):
        mock_return_values = [ConnectionResetError(), ConnectionResetError(), ConnectionResetError(),
                              ConnectionResetError(), ConnectionResetError()]
        mock_load_state_dict_from_url.side_effect = mock_return_values

        with pytest.raises(ConnectionResetError):
            PretrainedModelFactory._load_state_dict_from_url_with_retry(url="https://aka.ms/dummy_model.pth")
        assert mock_load_state_dict_from_url.call_count == PretrainedSettings.DOWNLOAD_RETRY_COUNT

        for i in range(len(mock_return_values) - 1):
            # please note that, sleep function called one less time than load_state_dict_from_url function
            wait_time = (2 ** i) * PretrainedSettings.BACKOFF_IN_SECONDS + mock_random.return_value
            assert mock_sleep.call_args_list[i] == call(wait_time)

    @patch("random.uniform", return_value=0.5)
    @patch("time.sleep", return_value=None)
    @patch("azureml.automl.dnn.vision.common.pretrained_model_utilities.load_state_dict_from_url")
    def test_load_state_dict_from_url_with_retry_partial_exceptions(self, mock_load_state_dict_from_url, mock_sleep,
                                                                    mock_random):
        """Scenario where first 3 download attempt results in ConnectionResetError and eventually download succeeded"""

        mock_return_values = [ConnectionResetError(), ConnectionResetError(), ConnectionResetError(), OrderedDict()]
        mock_load_state_dict_from_url.side_effect = mock_return_values
        return_value = PretrainedModelFactory._load_state_dict_from_url_with_retry(
            url="https://aka.ms/dummy_model.pth")
        assert type(return_value) == OrderedDict
        assert mock_load_state_dict_from_url.call_count == len(mock_return_values)
        for i in range(len(mock_return_values) - 1):
            # please note that, sleep function called one less time than load_state_dict_from_url function
            wait_time = (2 ** i) * PretrainedSettings.BACKOFF_IN_SECONDS + mock_random.return_value
            assert mock_sleep.call_args_list[i] == call(wait_time)
