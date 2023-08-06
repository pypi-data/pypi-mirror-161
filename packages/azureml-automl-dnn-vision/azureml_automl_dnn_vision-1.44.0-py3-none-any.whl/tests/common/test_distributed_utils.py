# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for distributed_utils.py"""

import logging
import os
import pytest

from unittest.mock import MagicMock, patch

from azureml.automl.core._logging import log_server
from azureml.automl.dnn.vision.common import distributed_utils
from azureml.automl.dnn.vision.common.constants import DistributedLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException, AutoMLVisionValidationException

import azureml.automl.dnn.vision.classification.runner as classification_runner
import azureml.automl.dnn.vision.object_detection.runner as od_runner
import azureml.automl.dnn.vision.object_detection_yolo.runner as od_yolo_runner


class TestDistributedUtils:

    @staticmethod
    def _mock_train_worker_fn_distributed_classification(rank, worker_settings, worker_mltable_data_json, multilabel):
        assert rank >= 0
        assert worker_settings[DistributedLiterals.DISTRIBUTED]
        assert worker_mltable_data_json == "dummy_mltable_data_json"
        assert not multilabel

    @staticmethod
    def _mock_train_worker_fn_distributed_od(rank, worker_settings, worker_mltable_data_json):
        assert rank >= 0
        assert worker_settings[DistributedLiterals.DISTRIBUTED]
        assert worker_mltable_data_json == "dummy_mltable_data_json"

    @pytest.mark.parametrize("runner_type", ("classification", "object_detection", "object_detection_yolo"))
    @patch("torch.cuda")
    def test_launch_single_or_distributed_training_non_distributed_scenario(self, torch_cuda_mock, runner_type):
        test_process_id = os.getpid()
        mltable_data_json = "dummy_mltable_data_json"
        multilabel = False
        device_count = 4
        logger = logging.getLogger("test_distributed_utils")

        if runner_type == "classification":
            expected_args = (0, {DistributedLiterals.DISTRIBUTED: False}, mltable_data_json, multilabel)
            additional_train_worker_args = (mltable_data_json, multilabel)
        else:
            expected_args = (0, {DistributedLiterals.DISTRIBUTED: False}, mltable_data_json)
            additional_train_worker_args = (mltable_data_json,)

        # Non distributed training scenario tests

        def _train_worker_fn_side_effect(*args, **kwargs):
            # train_worker function should be called in the same process in non-distributed training.
            assert os.getpid() == test_process_id

        train_worker_path = "azureml.automl.dnn.vision.{}.runner.train_worker".format(runner_type)
        with patch(train_worker_path) as mock_train_worker_fn:
            mock_train_worker_fn.side_effect = _train_worker_fn_side_effect

            if runner_type == "classification":
                train_worker_fn = classification_runner.train_worker
            else:
                if runner_type == "object_detection":
                    train_worker_fn = od_runner.train_worker
                else:
                    train_worker_fn = od_yolo_runner.train_worker

            non_distributed_scenarios = [
                # Distributed setting, cuda available, device count
                (True, False, 0),  # cuda not available
                (True, True, 1),  # cuda available, device count 1
                (False, True, device_count),  # cuda available, device count > 1, but settings["distributed"] is False
            ]

            for scenario in non_distributed_scenarios:
                settings = {DistributedLiterals.DISTRIBUTED: scenario[0]}
                torch_cuda_mock.is_available.return_value = scenario[1]
                torch_cuda_mock.device_count.return_value = scenario[2]
                distributed_utils.launch_single_or_distributed_training(settings, train_worker_fn,
                                                                        additional_train_worker_args, logger, None)
                assert not settings[DistributedLiterals.DISTRIBUTED]
                mock_train_worker_fn.assert_called_once()
                mock_train_worker_fn.assert_called_once_with(*expected_args)
                mock_train_worker_fn.reset_mock()

        # Distributed scenario tests
        def _update_settings_for_distributed_training_side_effect(fn_settings, fn_device_count, fn_node_count):
            assert fn_device_count == device_count

        if runner_type == "classification":
            train_worker_fn = TestDistributedUtils._mock_train_worker_fn_distributed_classification
        else:
            train_worker_fn = TestDistributedUtils._mock_train_worker_fn_distributed_od

        with patch("azureml.automl.dnn.vision.common.distributed_utils.update_settings_for_distributed_training") \
                as mock_update_settings_fn:
            mock_update_settings_fn.side_effect = _update_settings_for_distributed_training_side_effect

            # cuda available, device count > 1 -> Distributed training.
            settings = {DistributedLiterals.DISTRIBUTED: True}
            torch_cuda_mock.is_available.return_value = True
            torch_cuda_mock.device_count.return_value = device_count
            distributed_utils.launch_single_or_distributed_training(settings, train_worker_fn,
                                                                    additional_train_worker_args, logger, None)
            assert settings[DistributedLiterals.DISTRIBUTED]
            mock_update_settings_fn.reset_mock()

    @patch.dict(os.environ, {log_server.LOGFILE_ENV_NAME: "/tmp/debug.log"})
    @patch('azureml.automl.core._logging.log_server.set_log_file')
    def test_set_distributed_logging_rank(self, mock_set_log_file):
        distributed_utils._set_distributed_logging_rank(5)
        mock_set_log_file.assert_called_once_with(os.path.join('/tmp', 'debug-5.log'))

    @patch(distributed_utils.__name__ + '._get_node_count')
    @patch(distributed_utils.__name__ + '._get_device_count')
    @patch(distributed_utils.__name__ + '.update_settings_for_distributed_training')
    @patch('torch.multiprocessing.spawn')
    def test_launch_single_or_distributed_training_varying_world_size(
        self,
        torch_spawn_mock,
        mock_update_settings_for_distributed_training,
        mock__get_device_count,
        mock_get_node_count,
    ):
        # Define side effect for torch.multiprocessing.spawn mock to store call state
        num_spawned_processes = -1

        def torch_spawn_side_effect(_, nprocs, *args, **kwargs):
            nonlocal num_spawned_processes
            num_spawned_processes = nprocs
        torch_spawn_mock.side_effect = torch_spawn_side_effect

        # Define helper function to run test cases
        def helper_fn(
            node_count, device_count, distributed_enabled, multi_processes_should_be_spawned
        ):
            mock_get_node_count.return_value = node_count
            mock__get_device_count.return_value = device_count
            settings = {DistributedLiterals.DISTRIBUTED: distributed_enabled}
            mock_train_worker_fn = MagicMock()
            initial_torch_spawn_mock_call_count = torch_spawn_mock.call_count
            distributed_utils.launch_single_or_distributed_training(
                settings, mock_train_worker_fn, MagicMock(), MagicMock(), None)
            if multi_processes_should_be_spawned:
                assert settings[DistributedLiterals.DISTRIBUTED]
                assert torch_spawn_mock.call_count == initial_torch_spawn_mock_call_count + 1
                assert num_spawned_processes == device_count
                mock_train_worker_fn.assert_not_called()
            else:
                assert not settings[DistributedLiterals.DISTRIBUTED]
                assert torch_spawn_mock.call_count == initial_torch_spawn_mock_call_count
                mock_train_worker_fn.assert_called()

        helper_fn(node_count=1, device_count=1, distributed_enabled=True, multi_processes_should_be_spawned=False)
        helper_fn(node_count=1, device_count=2, distributed_enabled=True, multi_processes_should_be_spawned=True)
        helper_fn(node_count=1, device_count=2, distributed_enabled=False, multi_processes_should_be_spawned=False)
        helper_fn(node_count=1, device_count=0, distributed_enabled=True, multi_processes_should_be_spawned=False)
        helper_fn(node_count=1, device_count=0, distributed_enabled=False, multi_processes_should_be_spawned=False)
        with pytest.raises(AutoMLVisionValidationException):
            helper_fn(node_count=5, device_count=0, distributed_enabled=True, multi_processes_should_be_spawned=False)
        helper_fn(node_count=5, device_count=1, distributed_enabled=True, multi_processes_should_be_spawned=True)
        with pytest.raises(AutoMLVisionValidationException):
            helper_fn(node_count=5, device_count=1, distributed_enabled=False, multi_processes_should_be_spawned=True)

    @patch(distributed_utils.__name__ + '._get_device_count')
    @patch(distributed_utils.__name__ + '._get_node_rank')
    def test_calculate_rank(self, mock_get_node_rank, mock__get_device_count):
        def helper_fn(device_count, node_rank, local_rank, expected_rank):
            mock__get_device_count.return_value = device_count
            mock_get_node_rank.return_value = node_rank
            assert distributed_utils._calculate_rank(local_rank) == expected_rank

        helper_fn(device_count=1, node_rank=0, local_rank=0, expected_rank=0)
        helper_fn(device_count=1, node_rank=1, local_rank=0, expected_rank=1)
        helper_fn(device_count=1, node_rank=2, local_rank=0, expected_rank=2)
        helper_fn(device_count=4, node_rank=0, local_rank=0, expected_rank=0)
        helper_fn(device_count=4, node_rank=0, local_rank=1, expected_rank=1)
        helper_fn(device_count=4, node_rank=1, local_rank=0, expected_rank=4)
        helper_fn(device_count=4, node_rank=1, local_rank=1, expected_rank=5)

    def test_validate_multinode_run(self):
        distributed_utils._validate_multinode_run(True, 1, None)
        with pytest.raises(AutoMLVisionValidationException):
            distributed_utils._validate_multinode_run(True, 0, None)
        with pytest.raises(AutoMLVisionValidationException):
            distributed_utils._validate_multinode_run(False, 1, None)

    @patch('azureml.automl.dnn.vision.common.utils.post_warning')
    def test_validate_multinode_run_validate_ib_warning(self, mock_post_warning):
        with patch.dict(os.environ, {DistributedLiterals.NCCL_IB_DISABLE: '0'}):
            distributed_utils._validate_multinode_run(True, 1, None)
        mock_post_warning.assert_not_called()
        distributed_utils._validate_multinode_run(True, 1, None)
        mock_post_warning.assert_called()

    def test_get_master_addr_and_port_single_node(self):
        settings = {DistributedLiterals.MASTER_ADDR: 'master_addr', DistributedLiterals.MASTER_PORT: 'master_port'}
        master_addr, master_port = distributed_utils._get_master_addr_and_port(settings, 1)
        assert master_addr == 'master_addr'
        assert master_port == 'master_port'

    @patch.dict(os.environ, {
        DistributedLiterals.MASTER_ADDR: 'master_addr_env',
        DistributedLiterals.MASTER_PORT: 'master_port_env'})
    def test_get_master_addr_and_port_multi_node(self):
        settings = {DistributedLiterals.MASTER_ADDR: 'master_addr', DistributedLiterals.MASTER_PORT: 'master_port'}
        master_addr, master_port = distributed_utils._get_master_addr_and_port(settings, 2)
        assert master_addr == 'master_addr_env'
        assert master_port == 'master_port_env'

    @patch.dict(os.environ, {DistributedLiterals.MASTER_PORT: 'master_port_env'})
    def test_get_master_addr_and_port_multi_node_missing_master_addr_env_var(self):
        settings = {DistributedLiterals.MASTER_ADDR: 'master_addr', DistributedLiterals.MASTER_PORT: 'master_port'}
        with pytest.raises(AutoMLVisionSystemException):
            distributed_utils._get_master_addr_and_port(settings, 2)

    @patch.dict(os.environ, {DistributedLiterals.MASTER_ADDR: 'master_addr_env'})
    def test_get_master_addr_and_port_multi_node_missing_master_port_env_var(self):
        settings = {DistributedLiterals.MASTER_ADDR: 'master_addr', DistributedLiterals.MASTER_PORT: 'master_port'}
        with pytest.raises(AutoMLVisionSystemException):
            distributed_utils._get_master_addr_and_port(settings, 2)


if __name__ == "__main__":
    pytest.main(['-k', os.path.basename(__file__)])
