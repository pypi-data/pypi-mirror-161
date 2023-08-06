import os
from typing import Any

import boto3

from anyscale.authenticate import get_auth_api_client


"""anyscale/experimental_integrations.py: Experimental util functions for W&B integration and secret store prototypes."""

WANDB_API_KEY_NAME = "WANDB_API_KEY_NAME"


def get_aws_secret(secret_name: str, **kwargs) -> str:
    """
    Get secret value from AWS secrets manager.

    Arguments:
        secret_name: Key of your secret
        kwargs: Optional credentials passed in to authenticate instance
    """
    client = boto3.client("secretsmanager", **kwargs)
    response = client.get_secret_value(SecretId=secret_name)

    # Depending on whether the secret is a string or binary, one of these fields will be populated.
    if "SecretString" in response:
        secret = response.pop("SecretString")
    else:
        secret = response.pop("SecretBinary")

    # TODO(nikita): Return secret as a ProtectedString
    return secret


def wandb_setup_api_key_hook() -> str:
    """
    Returns W&B API key based on key set in WANDB_API_KEY_NAME in
    AWS secrets manager. This returns the API key in plain text,
    so take care to not save the output in any logs.

    Assumes instance is running with correct IAM role, so credentials
    don't have to be passed to access secrets manager.
    """
    secret_name = os.environ.get(WANDB_API_KEY_NAME)
    production_job_id = os.environ.get("ANYSCALE_PRODUCTION_JOB_ID")
    if not production_job_id:
        raise Exception(
            "ANYSCALE_PRODUCTION_JOB_ID environment variable not set. The W&B integration is "
            "currently only supported for production jobs."
        )

    api_client = get_auth_api_client(log_output=False).api_client
    production_job = api_client.get_job_api_v2_decorated_ha_jobs_production_job_id_get(
        production_job_id
    ).result

    if not secret_name:
        user_id = production_job.creator_id
        secret_name = f"wandb_api_key_{user_id}"

    # Get cloud from production job to verify job is using an AWS cloud and
    # to pass the region to the boto3 api.
    cluster_id = (
        production_job.state.cluster.id
        if (production_job.state and production_job.state.cluster)
        else None
    )
    if cluster_id:
        cluster = api_client.get_session_api_v2_sessions_session_id_get(
            cluster_id
        ).result
        cloud_id = cluster.cloud_id
        cloud = api_client.get_cloud_api_v2_clouds_cloud_id_get(cloud_id).result
    else:
        raise Exception(
            f"Unable to find cluster for production job {production_job_id}"
        )

    if cloud.provider != "AWS":
        raise Exception(
            "The Anyscale W&B integration is currently only supported for AWS clouds."
        )
    region = cloud.region

    secret = get_aws_secret(secret_name, region_name=region)
    return secret


def wandb_send_run_info_hook(run: Any) -> None:
    try:
        import wandb
    except ImportError:
        raise Exception("Unable to import wandb.")

    assert isinstance(
        run, wandb.sdk.wandb_run.Run
    ), "`run` argument must be of type wandb.sdk.wandb_run.Run"

    api_client = get_auth_api_client(log_output=False).api_client

    if os.environ.get("ANYSCALE_PRODUCTION_JOB_ID"):
        production_job_id = os.environ.get("ANYSCALE_PRODUCTION_JOB_ID")
        api_client.update_wandb_run_values_api_v2_experimental_integrations_update_wandb_run_values_production_job_id_get(
            production_job_id=production_job_id,
            wandb_entity=run.entity,
            wandb_project=run.project,
            wandb_group=run.group,
        )
