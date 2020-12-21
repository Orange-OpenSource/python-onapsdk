#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""NBI module."""
from abc import ABC
from enum import Enum
from typing import Iterator
from uuid import uuid4

from onapsdk.aai.business.customer import Customer
from onapsdk.exceptions import RequestError
from onapsdk.onap_service import OnapService
from onapsdk.utils import get_zulu_time_isoformat
from onapsdk.utils.jinja import jinja_env
from onapsdk.utils.mixins import WaitForFinishMixin


class Nbi(OnapService, ABC):
    """NBI base class."""

    base_url = "https://nbi.api.simpledemo.onap.org:30274"
    api_version = "/nbi/api/v4"

    @classmethod
    def is_status_ok(cls) -> bool:
        """Check NBI service status.

        Returns:
            bool: True if NBI works fine, False otherwise

        """
        try:
            cls.send_message(
                "GET",
                "Check NBI status",
                f"{cls.base_url}{cls.api_version}/status"
            )
        except RequestError as exc:
            msg = f"An error occured during NBI status check: {exc}"
            cls._logger.error(msg)
            return False
        return True


class ServiceSpecification(Nbi):
    """NBI service specification class."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 unique_id: str,
                 name: str,
                 invariant_uuid: str,
                 category: str,
                 distribution_status: str,
                 version: str,
                 lifecycle_status: str) -> None:
        """Service specification object initialization.

        Args:
            unique_id (str): Unique ID
            name (str): Service specification name
            invariant_uuid (str): Invariant UUID
            category (str): Category
            distribution_status (str): Service distribution status
            version (str): Service version
            lifecycle_status (str): Service lifecycle status
        """
        super().__init__()
        self.unique_id: str = unique_id
        self.name: str = name
        self.invariant_uuid: str = invariant_uuid
        self.category: str = category
        self.distribution_status: str = distribution_status
        self.version: str = version
        self.lifecycle_status: str = lifecycle_status

    def __repr__(self) -> str:
        """Service specification representation.

        Returns:
            str: Service specification object human readable representation

        """
        return (f"ServiceSpecification(unique_id={self.unique_id}, name={self.name}, "
                f"invariant_uuid={self.invariant_uuid}, category={self.category}, "
                f"distribution_status={self.distribution_status}, version={self.version}, "
                f"lifecycle_status={self.lifecycle_status})")

    @classmethod
    def get_all(cls) -> Iterator["ServiceSpecification"]:
        """Get all service specifications.

        Yields:
            ServiceSpecification: Service specification object

        """
        for service_specification in cls.send_message_json("GET",
                                                           "Get service specifications from NBI",
                                                           (f"{cls.base_url}{cls.api_version}/"
                                                            "serviceSpecification")):
            yield ServiceSpecification(
                service_specification.get("id"),
                service_specification.get("name"),
                service_specification.get("invariantUUID"),
                service_specification.get("category"),
                service_specification.get("distributionStatus"),
                service_specification.get("version"),
                service_specification.get("lifecycleStatus"),
            )

    @classmethod
    def get_by_id(cls, service_specification_id: str) -> "ServiceSpecification":
        """Get service specification by ID.

        Args:
            service_specification_id (str): Service specification ID

        Returns:
            ServiceSpecification: Service specification object

        """
        service_specification: dict = cls.send_message_json(
            "GET",
            f"Get service specification with {service_specification_id} ID from NBI",
            f"{cls.base_url}{cls.api_version}/serviceSpecification/{service_specification_id}"
        )
        return ServiceSpecification(
            service_specification.get("id"),
            service_specification.get("name"),
            service_specification.get("invariantUUID"),
            service_specification.get("category"),
            service_specification.get("distributionStatus"),
            service_specification.get("version"),
            service_specification.get("lifecycleStatus"),
        )


class Service(Nbi):
    """NBI service."""

    def __init__(self,  # pylint: disable=too-many-arguments
                 name: str,
                 service_id: str,
                 service_specification_name: str,
                 service_specification_id: str,
                 customer_id: str,
                 customer_role: str,
                 href: str) -> None:
        """Service object initialization.

        Args:
            name (str): Service name
            service_id (str): Service ID
            service_specification_name (str): Service specification name
            service_specification_id (str): Service specification ID
            customer_id (str): Global customer ID
            customer_role (str): Customer role
            href (str): Service object href
        """
        super().__init__()
        self.name: str = name
        self.service_id: str = service_id
        self._service_specification_name: str = service_specification_name
        self._service_specification_id: str = service_specification_id
        self._customer_id: str = customer_id
        self.customer_role: str = customer_role
        self.href: str = href

    def __repr__(self) -> str:
        """Service object representation.

        Returns:
            str: Human readable service object representation

        """
        return (f"Service(name={self.name}, service_id={self.service_id}, "
                f"service_specification={self.service_specification}, customer={self.customer}, "
                f"customer_role={self.customer_role})")

    @classmethod
    def get_all(cls) -> Iterator["Service"]:
        """Get all services.

        Yields:
            Service: Service object

        """
        for service in cls.send_message_json("GET",
                                             "Get service instances from NBI",
                                             f"{cls.base_url}{cls.api_version}/service"):
            yield cls(service.get("name"),
                      service.get("id"),
                      service.get("serviceSpecification", {}).get("name"),
                      service.get("serviceSpecification", {}).get("id"),
                      service.get("relatedParty", {}).get("id"),
                      service.get("relatedParty", {}).get("role"),
                      service.get("href"))

    @property
    def customer(self) -> Customer:
        """Service order Customer object.

        Returns:
            Customer: Customer object

        """
        if not self._customer_id:
            return None
        return Customer.get_by_global_customer_id(self._customer_id)

    @property
    def service_specification(self) -> ServiceSpecification:
        """Service specification.

        Returns:
            ServiceSpecification: Service specification object

        """
        if not self._service_specification_id:
            return None
        return ServiceSpecification.get_by_id(self._service_specification_id)


class ServiceOrder(Nbi, WaitForFinishMixin):  # pylint: disable=too-many-instance-attributes
    """Service order class."""

    WAIT_FOR_SLEEP_TIME = 10

    def __init__(self,  # pylint: disable=too-many-arguments
                 unique_id: str,
                 href: str,
                 priority: str,
                 description: str,
                 category: str,
                 external_id: str,
                 service_instance_name: str,
                 state: str = None,
                 customer: Customer = None,
                 customer_id: str = None,
                 service_specification: ServiceSpecification = None,
                 service_specification_id: str = None) -> None:
        """Service order object initialization.

        Args:
            unique_id (str): unique ID
            href (str): object's href
            priority (str): order priority
            description (str): order description
            category (str): category description
            external_id (str): external ID
            service_instance_name (str): name of service instance
            state (str, optional): instantiation state. Defaults to None.
            customer (Customer, optional): Customer object. Defaults to None.
            customer_id (str, optional): global customer ID. Defaults to None.
            service_specification (ServiceSpecification, optional): service specification object.
                Defaults to None.
            service_specification_id (str, optional): service specification ID. Defaults to None.
        """
        super().__init__()
        self.unique_id: str = unique_id
        self.href: str = href
        self.priority: str = priority
        self.category: str = category
        self.description: str = description
        self.external_id: str = external_id
        self._customer: Customer = customer
        self._customer_id: str = customer_id
        self._service_specification: ServiceSpecification = service_specification
        self._service_specification_id: str = service_specification_id
        self.service_instance_name: str = service_instance_name
        self.state: str = state

    class StatusEnum(Enum):
        """Status enum.

        Store possible statuses for service order:
            - completed,
            - failed,
            - inProgress.
        If instantiation has status which is not covered by these values
            `unknown` value is used.

        """

        ACKNOWLEDGED = "acknowledged"
        IN_PROGRESS = "inProgress"
        FAILED = "failed"
        COMPLETED = "completed"
        REJECTED = "rejected"
        UNKNOWN = "unknown"

    def __repr__(self) -> str:
        """Service order object representation.

        Returns:
            str: Service order object representation.

        """
        return (f"ServiceOrder(unique_id={self.unique_id}, href={self.href}, "
                f"priority={self.priority}, category={self.category}, "
                f"description={self.description}, external_id={self.external_id}, "
                f"customer={self.customer}, service_specification={self.service_specification}"
                f"service_instance_name={self.service_instance_name}, state={self.state})")

    @property
    def customer(self) -> Customer:
        """Get customer object used in service order.

        Returns:
            Customer: Customer object

        """
        if not self._customer:
            if not self._customer_id:
                self._logger.error("No customer ID")
                return None
            self._customer = Customer.get_by_global_customer_id(self._customer_id)
        return self._customer

    @property
    def service_specification(self) -> ServiceSpecification:
        """Service order service specification used in order item.

        Returns:
            ServiceSpecification: Service specification

        """
        if not self._service_specification:
            if not self._service_specification_id:
                self._logger.error("No service specification")
                return None
            self._service_specification = ServiceSpecification.\
                get_by_id(self._service_specification_id)
        return self._service_specification

    @classmethod
    def get_all(cls) -> Iterator["ServiceOrder"]:
        """Get all service orders.

        Returns:
            Iterator[ServiceOrder]: ServiceOrder object

        """
        for service_order in cls.send_message_json("GET",
                                                   "Get all service orders",
                                                   f"{cls.base_url}{cls.api_version}/serviceOrder"):
            service_order_related_party = None
            if service_order.get("relatedParty") is not None:
                service_order_related_party = service_order.get(
                    "relatedParty", [{}])[0].get("id")

            yield ServiceOrder(
                unique_id=service_order.get("id"),
                href=service_order.get("href"),
                priority=service_order.get("priority"),
                category=service_order.get("category"),
                description=service_order.get("description"),
                external_id=service_order.get("externalId"),
                customer_id=service_order_related_party,
                service_specification_id=service_order.get("orderItem", [{}])[0].get("service")\
                    .get("serviceSpecification").get("id"),
                service_instance_name=service_order.get("orderItem", [{}])[0].\
                    get("service", {}).get("name"),
                state=service_order.get("state")
            )

    @classmethod
    def create(cls,
               customer: Customer,
               service_specification: ServiceSpecification,
               name: str = None,
               external_id: str = None) -> "ServiceOrder":
        """Create service order.

        Returns:
            ServiceOrder: ServiceOrder object

        """
        if external_id is None:
            external_id = str(uuid4())
        if name is None:
            name = f"Python_ONAP_SDK_service_instance_{str(uuid4())}"
        response: dict = cls.send_message_json(
            "POST",
            "Add service instance via ServiceOrder API",
            f"{cls.base_url}{cls.api_version}/serviceOrder",
            data=jinja_env()
            .get_template("nbi_service_order_create.json.j2")
            .render(
                customer=customer,
                service_specification=service_specification,
                service_instance_name=name,
                external_id=external_id,
                request_time=get_zulu_time_isoformat()
            )
        )
        return cls(
            unique_id=response.get("id"),
            href=response.get("href"),
            priority=response.get("priority"),
            description=response.get("description"),
            category=response.get("category"),
            external_id=response.get("externalId"),
            customer=customer,
            service_specification=service_specification,
            service_instance_name=name
        )

    @property
    def status(self) -> "StatusEnum":
        """Service order instantiation status.

        It's populated by call Service order endpoint.

        Returns:
            StatusEnum: Service order status.

        """
        response: dict = self.send_message_json("GET",
                                                "Get service order status",
                                                (f"{self.base_url}{self.api_version}/"
                                                 f"serviceOrder/{self.unique_id}"))
        try:
            return self.StatusEnum(response.get("state"))
        except (KeyError, ValueError):
            self._logger.exception("Invalid status")
            return self.StatusEnum.UNKNOWN

    @property
    def completed(self) -> bool:
        """Store an information if service order is completed or not.

        Service orded is completed if it's status is COMPLETED.

        Returns:
            bool: True if service orded is completed, False otherwise.

        """
        return self.status == self.StatusEnum.COMPLETED

    @property
    def rejected(self) -> bool:
        """Store an information if service order is rejected or not.

        Service orded is completed if it's status is REJECTED.

        Returns:
            bool: True if service orded is rejected, False otherwise.

        """
        return self.status == self.StatusEnum.REJECTED

    @property
    def failed(self) -> bool:
        """Store an information if service order is failed or not.

        Service orded is completed if it's status is FAILED.

        Returns:
            bool: True if service orded is failed, False otherwise.

        """
        return self.status == self.StatusEnum.FAILED

    @property
    def finished(self) -> bool:
        """Store an information if service order is finished or not.

        Service orded is finished if it's status is not ACKNOWLEDGED or IN_PROGRESS.

        Returns:
            bool: True if service orded is finished, False otherwise.

        """
        return self.status not in [self.StatusEnum.ACKNOWLEDGED,
                                   self.StatusEnum.IN_PROGRESS]
