import os
from typing import Any, Dict
import unittest
from unittest.mock import Mock

import pytest

import anyscale.job


ha_job_id = "ha_job_id"
ray_job_id = "ray_job_id"
should_succeed = "should_succeed"
false_str = "False"
true_str = "True"


@pytest.mark.parametrize(
    "env",
    [
        {
            anyscale.job.ANYSCALE_HA_JOB_ID: "",
            anyscale.job.ANYSCALE_RAY_JOB_SUBMISSION_ID: "",
            should_succeed: false_str,  # this is necessary because the value type must be a string
        },
        {
            anyscale.job.ANYSCALE_HA_JOB_ID: ha_job_id,
            anyscale.job.ANYSCALE_RAY_JOB_SUBMISSION_ID: "",
            should_succeed: false_str,
        },
        {
            anyscale.job.ANYSCALE_HA_JOB_ID: "",
            anyscale.job.ANYSCALE_RAY_JOB_SUBMISSION_ID: ray_job_id,
            should_succeed: false_str,
        },
        {
            anyscale.job.ANYSCALE_HA_JOB_ID: ha_job_id,
            anyscale.job.ANYSCALE_RAY_JOB_SUBMISSION_ID: ray_job_id,
            should_succeed: true_str,
        },
    ],
)
def test_get_env_vars(env):
    with unittest.mock.patch.dict(os.environ, env, clear=True):
        ids = anyscale.job._get_ha_job_id_from_environment()
        assert (
            (ha_job_id, ray_job_id) if env[should_succeed] == true_str else ids is None
        )


def test_submit_output_not_dict():
    anyscale.job._submit_raw_output = Mock()
    anyscale.job.logger = Mock()

    # Don't submit the output unless it is a dict
    anyscale.job.output("abcd", _fail_on_error=True)  # type: ignore
    anyscale.job.output([], _fail_on_error=True)  # type: ignore
    anyscale.job._submit_raw_output.assert_not_called()


def test_submit_output_not_serializable():
    anyscale.job._submit_raw_output = Mock()
    anyscale.job.logger = Mock()
    # Don't fail if the output is not JSON serializable
    circular: Dict[str, Any] = {}
    circular["key"] = circular
    anyscale.job.output(circular, _fail_on_error=True)
    anyscale.job._submit_raw_output.assert_not_called()
    anyscale.job.logger.warn.assert_called_once_with(
        "Failed to serialize the job output to JSON. Output will not be recorded."
    )


def test_submit_output_env_not_set():
    anyscale.job._submit_raw_output = Mock()
    anyscale.job.logger = Mock()
    # Don't submit if the env isn't set
    data = {"key": "value"}
    os.environ[anyscale.job.ANYSCALE_HA_JOB_ID] = ""
    os.environ[anyscale.job.ANYSCALE_RAY_JOB_SUBMISSION_ID] = ""
    anyscale.job.output(data, _fail_on_error=True)
    anyscale.job._submit_raw_output.assert_not_called()


def test_submit_output_api_exception():
    anyscale.job._submit_raw_output = Mock()
    anyscale.job.logger = Mock()

    # Do not raise an exception if the API returns an exception
    anyscale.job._submit_raw_output.side_effect = lambda *args, **kwargs: Exception(
        "test"
    )
    data = {"key": "value"}
    os.environ[anyscale.job.ANYSCALE_HA_JOB_ID] = ha_job_id
    os.environ[anyscale.job.ANYSCALE_RAY_JOB_SUBMISSION_ID] = ray_job_id
    anyscale.job.output(data, _fail_on_error=True)
    anyscale.job._submit_raw_output.assert_called_once_with(
        ha_job_id, ray_job_id, data, api_client=None
    )


def test_submit_output():
    anyscale.job._submit_raw_output = Mock()
    anyscale.job.logger = Mock()
    anyscale.job._submit_raw_output.reset_mock()
    # Do submit
    data = {"key": "value"}
    os.environ[anyscale.job.ANYSCALE_HA_JOB_ID] = ha_job_id
    os.environ[anyscale.job.ANYSCALE_RAY_JOB_SUBMISSION_ID] = ray_job_id
    anyscale.job.output(data, _fail_on_error=True)
    anyscale.job._submit_raw_output.assert_called_once_with(
        ha_job_id, ray_job_id, data, api_client=None
    )
