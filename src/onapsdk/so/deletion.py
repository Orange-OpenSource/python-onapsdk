#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Deletion module."""
from abc import ABC

from onapsdk.onap_service import OnapService
from onapsdk.utils.headers_creator import headers_so_creator
from onapsdk.utils.jinja import jinja_env

from onapsdk.so.so_element import OrchestrationRequest


class DeletionRequest(OrchestrationRequest, ABC):
    """Deletion request base class."""

    @classmethod
    def send_request(cls, instance: "AaiElement", use_vnf_api: bool = False) -> "Deletion":
        """Abstract method to send instance deletion request.

        Raises:
            NotImplementedError: Needs to be implemented in inheriting classes

        """
        raise NotImplementedError


class VfModuleDeletionRequest(DeletionRequest):  # pylint: disable=R0903
    """VF module deletion class."""

    @classmethod
    def send_request(cls,
                     instance: "VfModuleInstance",
                     use_vnf_api: bool = False) -> "VfModuleDeletion":
        """Send request to SO to delete VNF instance.

        Args:
            vnf_instance (VnfInstance): VNF instance to delete
            use_vnf_api (bool, optional): Flague to determine if VNF_API or GR_API
                should be used to deletion. Defaults to False.

        Returns:
            VnfDeletionRequest: Deletion request object

        """
        cls._logger.debug("VF module %s deletion request", instance.vf_module_id)
        response = cls.send_message_json("DELETE",
                                         (f"Create {instance.vf_module_id} VF module"
                                          "deletion request"),
                                         (f"{cls.base_url}/onap/so/infra/"
                                          f"serviceInstantiation/{cls.api_version}/"
                                          "serviceInstances/"
                                          f"{instance.vnf_instance.service_instance.instance_id}/"
                                          f"vnfs/{instance.vnf_instance.vnf_id}/"
                                          f"vfModules/{instance.vf_module_id}"),
                                         data=jinja_env().
                                         get_template("deletion_vf_module.json.j2").
                                         render(vf_module_instance=instance,
                                                use_vnf_api=use_vnf_api),
                                         exception=ValueError,
                                         headers=headers_so_creator(OnapService.headers))
        return cls(request_id=response["requestReferences"]["requestId"])


class VnfDeletionRequest(DeletionRequest):  # pylint: disable=R0903
    """VNF deletion class."""

    @classmethod
    def send_request(cls,
                     instance: "VnfInstance",
                     use_vnf_api: bool = False) -> "VnfDeletionRequest":
        """Send request to SO to delete VNF instance.

        Args:
            instance (VnfInstance): VNF instance to delete
            use_vnf_api (bool, optional): Flague to determine if VNF_API or GR_API
                should be used to deletion. Defaults to False.

        Returns:
            VnfDeletionRequest: Deletion request object

        """
        cls._logger.debug("VNF %s deletion request", instance.vnf_id)
        response = cls.send_message_json("DELETE",
                                         f"Create {instance.vnf_id} VNF deletion request",
                                         (f"{cls.base_url}/onap/so/infra/"
                                          f"serviceInstantiation/{cls.api_version}/"
                                          "serviceInstances/"
                                          f"{instance.service_instance.instance_id}/"
                                          f"vnfs/{instance.vnf_id}"),
                                         data=jinja_env().
                                         get_template("deletion_vnf.json.j2").
                                         render(vnf_instance=instance,
                                                use_vnf_api=use_vnf_api),
                                         exception=ValueError,
                                         headers=headers_so_creator(OnapService.headers))
        return cls(request_id=response["requestReferences"]["requestId"])


class ServiceDeletionRequest(DeletionRequest):  # pylint: disable=R0903
    """Service deletion request class."""

    @classmethod
    def send_request(cls,
                     instance: "ServiceInstance",
                     use_vnf_api: bool = False) -> "ServiceDeletionRequest":
        """Send request to SO to delete service instance.

        Args:
            instance (ServiceInstance): service instance to delete
            use_vnf_api (bool, optional): Flague to determine if VNF_API or GR_API
                should be used to deletion. Defaults to False.

        Returns:
            ServiceDeletionRequest: Deletion request object

        """
        cls._logger.debug("Service %s deletion request", instance.instance_id)
        response = cls.send_message_json("DELETE",
                                         f"Create {instance.instance_id} Service deletion request",
                                         (f"{cls.base_url}/onap/so/infra/"
                                          f"serviceInstantiation/{cls.api_version}/"
                                          f"serviceInstances/{instance.instance_id}"),
                                         data=jinja_env().
                                         get_template("deletion_service.json.j2").
                                         render(service_instance=instance,
                                                use_vnf_api=use_vnf_api),
                                         exception=ValueError,
                                         headers=headers_so_creator(OnapService.headers))
        return cls(request_id=response["requestReferences"]["requestId"])
