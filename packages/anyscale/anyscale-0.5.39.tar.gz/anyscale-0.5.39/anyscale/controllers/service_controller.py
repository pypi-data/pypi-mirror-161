from datetime import datetime
import enum
import os
from typing import Any, Dict, List, Optional

import click
from pydantic import Field
import yaml

from anyscale.cli_logger import BlockLogger
from anyscale.client.openapi_client import (
    ComputeTemplate,
    CreateProductionService,
    ProductionJob,
    ProductionJobConfig,
)
from anyscale.controllers.base_controller import BaseController
from anyscale.controllers.job_controller import JobConfig, JobController
from anyscale.project import infer_project_id
from anyscale.util import get_endpoint, is_anyscale_workspace
from anyscale.utils.runtime_env import override_runtime_env_for_local_working_dir


class UserServiceAccessTypes(str, enum.Enum):
    private = "private"
    public = "public"


class ServiceConfig(JobConfig):
    healthcheck_url: str = Field(..., description="Healthcheck url for service.")
    access: UserServiceAccessTypes = Field(
        UserServiceAccessTypes.public,
        description=(
            "Whether user service (eg: serve deployment) can be accessed by public "
            "internet traffic. If public, a user service endpoint can be queried from "
            "the public internet with the provided authentication token. "
            "If private, the user service endpoint can only be queried from within "
            "the same Anyscale cloud and will not require an authentication token."
        ),
    )


class ServiceController(BaseController):
    def __init__(
        self, log: BlockLogger = BlockLogger(), initialize_auth_api_client: bool = True
    ):
        super().__init__(initialize_auth_api_client=initialize_auth_api_client)
        self.log = log
        self.job_controller = JobController(
            initialize_auth_api_client=initialize_auth_api_client
        )

    def deploy(
        self,
        service_config_file: str,
        name: Optional[str],
        description: Optional[str],
        healthcheck_url: Optional[str] = None,
        is_entrypoint_cmd: Optional[bool] = False,
        entrypoint: Optional[List[str]] = None,
    ) -> None:
        entrypoint = entrypoint or []
        if is_anyscale_workspace() and is_entrypoint_cmd:
            entrypoint = [service_config_file, *entrypoint]
            config = self.generate_config_from_entrypoint(
                entrypoint, name, description, healthcheck_url=healthcheck_url
            )
            self.deploy_from_config(config)
        elif len(entrypoint) == 0:
            # Assume that job_config_file is a file and submit it.
            config = self.generate_config_from_file(
                service_config_file, name, description, healthcheck_url=healthcheck_url,
            )
            self.deploy_from_config(config)
        elif len(entrypoint) != 0:
            msg = (
                "Within an Anyscale Workspace, `anyscale service deploy` takes either a file, or a command. To submit a command, use `anyscale service deploy -- my command`."
                if is_anyscale_workspace()
                else "`anyscale service deploy` takes one argument, a YAML file configuration. Please use `anyscale service deploy my_file`."
            )
            raise click.ClickException(msg)

    def generate_config_from_entrypoint(
        self,
        entrypoint: List[str],
        name: Optional[str],
        description: Optional[str],
        healthcheck_url: Optional[str] = None,
    ) -> ServiceConfig:
        config_dict = {
            "entrypoint": " ".join(entrypoint),
            "name": name,
            "description": description,
            "healthcheck_url": healthcheck_url,
        }
        return self._populate_service_config(config_dict)

    def generate_config_from_file(
        self,
        service_config_file,
        name: Optional[str],
        description: Optional[str],
        healthcheck_url: Optional[str] = None,
    ) -> ServiceConfig:
        if not os.path.exists(service_config_file):
            raise click.ClickException(f"Config file {service_config_file} not found.")

        with open(service_config_file, "r") as f:
            config_dict = yaml.safe_load(f)

        service_config = self._populate_service_config(config_dict)
        if name:
            service_config.name = name

        if description:
            service_config.description = description

        if healthcheck_url:
            service_config.healthcheck_url = healthcheck_url

        return service_config

    def deploy_from_config(self, service_config: ServiceConfig):
        project_id = infer_project_id(
            service_config.project_id, self.anyscale_api_client, self.log
        )

        service_config.runtime_env = override_runtime_env_for_local_working_dir(
            service_config.runtime_env, self.log
        )

        config_object = ProductionJobConfig(
            entrypoint=service_config.entrypoint,
            runtime_env=service_config.runtime_env,
            build_id=service_config.build_id,
            compute_config_id=service_config.compute_config_id,
            max_retries=service_config.max_retries,
        )

        service = self.api_client.apply_service_api_v2_decorated_ha_jobs_apply_service_put(
            CreateProductionService(
                name=service_config.name
                or "cli-job-{}".format(datetime.now().isoformat()),
                description=service_config.description or "Service updated from CLI",
                project_id=project_id,
                config=config_object,
                healthcheck_url=service_config.healthcheck_url,
                access=service_config.access,
            )
        ).result

        maximum_uptime_minutes = self._get_maximum_uptime_minutes(service)
        self.log.info(
            f"Maximum uptime is {self._get_maximum_uptime_output(maximum_uptime_minutes)} for clusters launched by this service."
            f"{self._get_additional_log_if_maximum_uptime_enabled(maximum_uptime_minutes)}"
        )
        self.log.info(
            f"Service {service.id} has been deployed. Current state of service: {service.state.current_state}."
        )
        self.log.info(
            f"Query the status of the service with `anyscale service list --service-id {service.id}`."
        )
        self.log.info(
            f'View the service in the UI at {get_endpoint(f"/services/{service.id}")}.'
        )

    def _get_maximum_uptime_minutes(self, service: ProductionJob) -> Optional[int]:
        compute_config: ComputeTemplate = self.api_client.get_compute_template_api_v2_compute_templates_template_id_get(
            service.config.compute_config_id
        ).result
        return compute_config.config.maximum_uptime_minutes

    def _get_maximum_uptime_output(self, maximum_uptime_minutes: Optional[int]) -> str:
        if maximum_uptime_minutes and maximum_uptime_minutes > 0:
            return f"set to {maximum_uptime_minutes} minutes"
        return "disabled"

    def _get_additional_log_if_maximum_uptime_enabled(
        self, maximum_uptime_minutes: Optional[int]
    ) -> str:
        if maximum_uptime_minutes and maximum_uptime_minutes > 0:
            return " This may cause disruptions. To disable, update the compute config."
        return ""

    def _populate_service_config(self, config_dict: Dict[str, Any]) -> ServiceConfig:
        if "ANYSCALE_EXPERIMENTAL_WORKSPACE_ID" in os.environ:
            if "ANYSCALE_SESSION_ID" in os.environ:
                cluster = self.anyscale_api_client.get_cluster(
                    os.environ["ANYSCALE_SESSION_ID"]
                ).result
                # If the job configs are not specified, infer them from the workspace:
                if "build_id" not in config_dict and "cluster_env" not in config_dict:
                    config_dict["build_id"] = cluster.cluster_environment_build_id
                if "project_id" not in config_dict:
                    config_dict["project_id"] = cluster.project_id
                if (
                    "compute_config" not in config_dict
                    and "compute_config_id" not in config_dict
                ):
                    config_dict["compute_config_id"] = cluster.cluster_compute_id

        service_config = ServiceConfig.parse_obj(config_dict)
        return service_config

    def list(
        self,
        include_all_users: bool,
        include_archived: bool,
        name: Optional[str],
        service_id: Optional[str],
        project_id: Optional[str],
        max_items: int,
    ) -> None:
        self.job_controller.list(
            include_all_users,
            name,
            service_id,
            project_id,
            include_archived=include_archived,
            max_items=max_items,
            is_service=True,
        )

    def archive(self, service_id: Optional[str], service_name: Optional[str]) -> None:
        self.job_controller.archive(service_id, service_name, is_service=True)

    def terminate(self, service_id: Optional[str], service_name: Optional[str]) -> None:
        self.job_controller.terminate(service_id, service_name, is_service=True)
