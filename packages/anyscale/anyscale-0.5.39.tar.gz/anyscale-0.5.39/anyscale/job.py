import json
import logging
import os
import traceback
from typing import Any, Dict, Optional, Tuple

from anyscale.authenticate import get_auth_api_client
from anyscale.util import str_data_size


logger = logging.getLogger("Job Outputs")

ANYSCALE_HA_JOB_ID = "ANYSCALE_HA_JOB_ID"
ANYSCALE_RAY_JOB_SUBMISSION_ID = "ANYSCALE_RAY_JOB_SUBMISSION_ID"


def output(result: Dict[str, Any], *, _api_client=None, _fail_on_error=False):
    """Submit the output for an Anyscale Production Job

    Outputs can only be recorded from within an Anyscale Production Job.

    This function should be called from the driver of your ray script.

    Example usage for this function can be found in the Anyscale documentation.

    Args:
        result (Dict[str, Any]): A JSON serializable dictionary representing your output data. Size limit is 1MiB.

    Raises:
        e: if the internal flag _fail_on_error is set, this function will raise any exceptions from the API
    """
    try:
        if not isinstance(result, dict):
            logger.warn(
                "The output of your function must be a dictionary. Your structured output will not be recorded."
            )
            return

        try:
            serialized_result = json.dumps(result, indent=2)
        except Exception:
            traceback.print_exc()
            logger.warn(
                "Failed to serialize the job output to JSON. Output will not be recorded."
            )
            return

        if str_data_size(serialized_result) > 1024 ** 2:
            logger.warn(
                "Job output exceeds maximum size of 1MiB. Output will not be recorded."
            )
            return

        # Check if we're in a production job last so we still go through the above checks
        # to aid users with debugging.
        ids = _get_ha_job_id_from_environment()
        if ids is None:
            logger.warn(
                "Job outputs can only be recorded from Production Jobs. Output will be ignored."
            )
            return

        ha_job_id, ray_job_submission_id = ids
        _submit_raw_output(
            ha_job_id, ray_job_submission_id, result, api_client=_api_client
        )
    except Exception as e:
        # Only crash the program if we have explicitly set the flag
        if _fail_on_error:
            raise e from None
        else:
            logger.warn(
                f"Your structured output was not recorded because of an error: {e}"
            )


def _submit_raw_output(
    ha_job_id: str,
    ray_job_submission_id: str,
    output: Dict[str, Any],
    *,
    api_client=None,
):
    if api_client is None:
        api_client = get_auth_api_client().api_client
    return api_client.create_structured_output_api_v2_structured_outputs_post(
        {
            "production_job_id": ha_job_id,
            "output": output,
            "ray_job_submission_id": ray_job_submission_id,
        }
    )


def _get_ha_job_id_from_environment() -> Optional[Tuple[str, str]]:
    ha_job_id = os.getenv(ANYSCALE_HA_JOB_ID)
    ray_job_submission_id = os.getenv(ANYSCALE_RAY_JOB_SUBMISSION_ID)

    if not ha_job_id:
        logger.debug(f"{ANYSCALE_HA_JOB_ID} env var not set.")

    if not ray_job_submission_id:
        logger.debug(f"{ANYSCALE_RAY_JOB_SUBMISSION_ID} env var not set.")

    if ha_job_id and ray_job_submission_id:
        return ha_job_id, ray_job_submission_id

    return None
