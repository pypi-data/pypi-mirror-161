from typing import Any, Dict, List, Optional

from ray.autoscaler._private.gcp.config import get_node_type
from ray.autoscaler._private.gcp.node import GCPNode
from ray.autoscaler._private.gcp.node_provider import GCPNodeProvider

from anyscale.autoscaler.node_provided_cache import NodeProviderCache


node_cache = NodeProviderCache()


class AnyscaleGCPNodeProvider(GCPNodeProvider):  # type: ignore
    def __init__(self, provider_config: Dict[str, Any], cluster_name: str) -> None:
        super().__init__(provider_config, cluster_name)

        self.provider_cache = node_cache

    def create_node(
        self, node_config: Dict[str, Any], tags: Dict[str, str], count: int
    ) -> Dict[str, Dict[str, str]]:
        """Override parent implementation.

        The logic around GCP is exactly the same, but instance_id should be
        returned, which cannot be accessed by calling the parent method.
        """
        with self.lock:
            labels = tags  # gcp uses "labels" instead of aws "tags"

            node_type = get_node_type(node_config)
            resource = self.resources[node_type]

            gcp_result = resource.create_instances(node_config, labels, count)
            instance_dict: Dict[str, Dict[str, str]] = {}
            for _, instance_id in gcp_result:
                # create_instances does not provide "PublicIpAddress"
                public_ip_address = super().external_ip(instance_id)
                instance_dict[instance_id] = {"PublicIpAddress": public_ip_address}

            return instance_dict

    def non_terminated_nodes(self, tag_filters: Dict[str, str]) -> List[str]:
        """Override parent implementation.

        The logic around GCP is exactly the same, but access to the nodes is needed to handle cache
        properly, which cannot be accessed by calling the parent method.
        """
        with self.lock:
            instances = []

            for resource in self.resources.values():
                node_instances = resource.list_instances(tag_filters)
                instances += node_instances

            # Note: All the operations use "name" as the unique instance id
            # Clear and re-populate cache.
            self.provider_cache.cleanup()
            for instance in instances:
                self.provider_cache.set_node(instance["name"], instance)
                labels = instance.get_labels()
                self.provider_cache.set_tags(instance["name"], labels)

            return [instance["name"] for instance in instances]

    def set_node_tags(self, node_id: str, node_tags: Dict[Any, Any]) -> None:
        super().set_node_tags(node_id=node_id, tags=node_tags)

        # Populate cache.
        self.provider_cache.set_tags(node_id, node_tags)

    def node_tags(self, node_id: str) -> Dict[Any, Any]:
        # Check cache first.
        if self.provider_cache.tags_exist(node_id):
            return self.provider_cache.get_tags(node_id)

        instance = super()._get_cached_node(node_id)

        # Populate cache.
        self.provider_cache.set_node(node_id, instance)
        labels = instance.get_labels()
        self.provider_cache.set_tags(instance["name"], labels)

        return labels

    def terminate_node(self, node_id: str) -> Dict[Any, Any]:
        # Delete from cache.
        self.provider_cache.delete_node_and_tags(node_id)

        result = super().terminate_node(node_id)
        return result

    def terminate_nodes(self, node_ids: List[str]) -> Optional[Dict[str, Any]]:
        # Delete from cache.
        for node_id in node_ids:
            self.provider_cache.delete_node_and_tags(node_id)

        result = super().terminate_nodes(node_ids)
        return result

    def _get_node(self, node_id: str) -> GCPNode:
        # Side effect: clear and updates cache of all nodes.
        instance = super()._get_node(node_id)

        # Populate cache.
        self.provider_cache.set_node(node_id, instance)
        labels = instance.get_labels()
        self.provider_cache.set_tags(instance["name"], labels)

        return instance

    def _get_cached_node(self, node_id: str) -> GCPNode:
        # Check cache first.
        if self.provider_cache.node_exists(node_id):
            return self.provider_cache.get_node(node_id)

        instance = super()._get_cached_node(node_id)

        # Populate cache.
        self.provider_cache.set_node(node_id, instance)
        labels = instance.get_labels()
        self.provider_cache.set_tags(instance["name"], labels)

        return instance

    def prepare_for_head_node(self, cluster_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        * Just return cluster_config for now, unless similar credential
            issues for AWS also happen for GCP (i.e. see prepare_for_head_node() in
            frontend/cli/anyscale/autoscaler/aws/node_provider.py)
        """

        return cluster_config

    def describe_instances(self, node_ids: List[str]) -> Any:
        """Left describe_instances here to to be backward compatible
        (i.e. mimic AnyscaleAWSNodeProvider interface), which is AWS-specific logic
        """
        raise NotImplementedError

    def describe_gcp_instances(self, node_ids: List[str]) -> Dict[str, str]:
        """To mimic describe_instances in AnyscaleAWSNodeProvider.
        TODO: Should move the operation logic to GCPResource/GCPCompute/GCPTPU instead
        """
        with self.lock:
            instances: Dict[str, str] = {}
            for node_id in node_ids:
                resource = self._get_resource_depending_on_node_name(node_id)
                instance = (
                    resource.resource.instances()
                    .get(
                        project=self.provider_config["project_id"],
                        zone=self.provider_config["availability_zone"],
                        instance=node_id,
                    )
                    .execute()
                )

                instances[node_id] = instance

            return instances

    def start_nodes(
        self, node_ids: List[str], wait_for_operation: bool = True
    ) -> Dict[str, str]:
        """To mimic AnyscaleAWSNodeProvider
        TODO: Should move the operation logic to GCPResource/GCPCompute/GCPTPU instead
        """
        with self.lock:
            results: Dict[str, str] = {}
            for node_id in node_ids:
                resource = self._get_resource_depending_on_node_name(node_id)
                operation = (
                    resource.resource.instances()
                    .start(
                        project=self.provider_config["project_id"],
                        zone=self.provider_config["availability_zone"],
                        instance=node_id,
                    )
                    .execute()
                )

                if wait_for_operation:
                    result = resource.wait_for_operation(operation)
                else:
                    result = operation

                results[node_id] = result

            return results

    def stop_nodes(
        self, node_ids: List[str], wait_for_operation: bool = True
    ) -> Dict[str, str]:
        """To mimic AnyscaleAWSNodeProvider
        TODO: Should move the operation logic to GCPResource/GCPCompute/GCPTPU instead
        """
        with self.lock:
            results: Dict[str, str] = {}
            for node_id in node_ids:
                resource = self._get_resource_depending_on_node_name(node_id)
                operation = (
                    resource.resource.instances()
                    .stop(
                        project=self.provider_config["project_id"],
                        zone=self.provider_config["availability_zone"],
                        instance=node_id,
                    )
                    .execute()
                )

                if wait_for_operation:
                    # stop nodes takes a long time
                    result = resource.wait_for_operation(operation, max_polls=36)
                else:
                    result = operation

                results[node_id] = result

            return results
