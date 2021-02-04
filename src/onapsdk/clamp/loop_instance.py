#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""Control Loop module."""
import json
from pathlib import Path
from jsonschema import validate, ValidationError

from onapsdk.clamp.clamp_element import Clamp
from onapsdk.utils.jinja import jinja_env
from onapsdk.exceptions import ParameterError

CLAMP_UPDDATE_REFRESH_TIMER = 60

class LoopInstance(Clamp):
    """Control Loop instantiation class."""

    # class variable
    _loop_schema = None
    operational_policies = ""

    def __init__(self, template: str, name: str, details: dict) -> None:
        """
        Initialize loop instance object.

        Args:
            template (str): template from which we build the loop
            name (str) : loop creation name
            details (dict) : dictionnary containing all loop details

        """
        super().__init__()
        self.template = template
        self.name = "LOOP_" + name
        self._details = details

    @property
    def details(self) -> dict:
        """Return and lazy load the details."""
        if not self._details:
            self._update_loop_details()
        return self._details

    @details.setter
    def details(self, details: dict) -> None:
        """Set value for details."""
        self._details = details

    def _update_loop_details(self) -> dict:
        """
        Update loop details.

        Returns:
            the dictionnary of loop details

        """
        url = f"{self.base_url()}/loop/{self.name}"
        loop_details = self.send_message_json('GET',
                                              'Get loop details',
                                              url)
        return loop_details

    def refresh_status(self) -> None:
        """Reshresh loop status."""
        url = f"{self.base_url()}/loop/getstatus/{self.name}"
        loop_details = self.send_message_json('GET',
                                              'Get loop status',
                                              url)

        self.details = loop_details

    @property
    def loop_schema(self) -> dict:
        """
        Return and lazy load the details schema.

        Returns:
            schema to be respected to accede to loop details

        """
        if not self._loop_schema:
            schema_file = Path.cwd() / 'src' / 'onapsdk' / 'clamp' / 'schema_details.json'
            with open(schema_file, "rb") as plan:
                self._loop_schema = json.load(plan)
        return self._loop_schema

    def validate_details(self) -> bool:
        """
        Validate Loop Instance details.

        Returns:
            schema validation status (True, False)

        """
        try:
            validate(self.details, self.loop_schema)
        except ValidationError as error:
            self._logger.error(error)
            self._logger.error("---------")
            self._logger.error(error.absolute_path)
            self._logger.error("---------")
            self._logger.error(error.absolute_schema_path)
            return False
        return True

    def create(self) -> None:
        """Create instance and load loop details."""
        url = f"{self.base_url()}/loop/create/{self.name}?templateName={self.template}"
        instance_details = self.send_message_json('POST',
                                                  'Create Loop Instance',
                                                  url)
        self.details = instance_details

    def add_operational_policy(self, policy_type: str, policy_version: str) -> None:
        """
        Add operational policy to the loop instance.

        Args:
            policy_type (str): the full policy model type
            policy_version (str): policy version

        Raises:
            ParameterError : Corrupt response or a key in a dictionary not found.
                It will also be raised when the response contains more operational
                policies than there are currently.

        """
        url = (f"{self.base_url()}/loop/addOperationaPolicy/{self.name}/"
               f"policyModel/{policy_type}/{policy_version}")
        add_response = self.send_message_json('PUT',
                                              'Create Operational Policy',
                                              url)

        key = "operationalPolicies"

        try:
            if self.details[key] is None:
                self.details[key] = []

            response_policies = add_response[key]
            current_policies = self.details[key]
        except KeyError as exc:
            msg = 'Corrupt response, current loop details. Key not found.'
            raise ParameterError(msg) from exc

        if len(response_policies) > len(current_policies):
            self.details = add_response
        else:
            raise ParameterError("Couldn't add the operational policy.")

    def remove_operational_policy(self, policy_type: str, policy_version: str) -> None:
        """
        Remove operational policy from the loop instance.

        Args:
            policy_type (str): the full policy model type
            policy_version (str): policy version

        """
        url = (f"{self.base_url()}/loop/removeOperationaPolicy/"
               f"{self.name}/policyModel/{policy_type}/{policy_version}")
        self.details = self.send_message_json('PUT',
                                              'Remove Operational Policy',
                                              url)

    def update_microservice_policy(self) -> None:
        """
        Update microservice policy configuration.

        Update microservice policy configuration using payload data.

        """
        url = f"{self.base_url()}/loop/updateMicroservicePolicy/{self.name}"
        template = jinja_env().get_template("clamp_add_tca_config.json.j2")
        microservice_name = self.details["globalPropertiesJson"]["dcaeDeployParameters"]\
                                        ["uniqueBlueprintParameters"]["policy_id"]
        data = template.render(name=microservice_name,
                               LOOP_name=self.name)

        self.send_message('POST',
                          'ADD TCA config',
                          url,
                          data=data)

    def extract_operational_policy_name(self, policy_type: str) -> str:
        """
        Return operational policy name for a closed loop and a given policy.

        Args:
            policy_type (str): the policy acronym.

        Raises:
            ParameterError : Couldn't load the operational policy name.

        Returns:
            Operational policy name in the loop details after adding a policy.

        """
        for policy in filter(lambda x: x["policyModel"]["policyAcronym"] == policy_type,
                             self.details["operationalPolicies"]):
            return policy["name"]

        raise ParameterError("Couldn't load the operational policy name.")

    def add_drools_conf(self) -> dict:
        """Add drools configuration."""
        self.validate_details()
        vfmodule_dicts = self.details["modelService"]["resourceDetails"]["VFModule"]
        entity_ids = {}
        #Get the vf module details
        for vfmodule in vfmodule_dicts.values():
            entity_ids["resourceID"] = vfmodule["vfModuleModelName"]
            entity_ids["modelInvariantId"] = vfmodule["vfModuleModelInvariantUUID"]
            entity_ids["modelVersionId"] = vfmodule["vfModuleModelUUID"]
            entity_ids["modelName"] = vfmodule["vfModuleModelName"]
            entity_ids["modelVersion"] = vfmodule["vfModuleModelVersion"]
            entity_ids["modelCustomizationId"] = vfmodule["vfModuleModelCustomizationUUID"]
        template = jinja_env().get_template("clamp_add_drools_policy.json.j2")
        data = template.render(name=self.extract_operational_policy_name("Drools"),
                               resourceID=entity_ids["resourceID"],
                               modelInvariantId=entity_ids["modelInvariantId"],
                               modelVersionId=entity_ids["modelVersionId"],
                               modelName=entity_ids["modelName"],
                               modelVersion=entity_ids["modelVersion"],
                               modelCustomizationId=entity_ids["modelCustomizationId"],
                               LOOP_name=self.name)
        return data

    def add_minmax_config(self) -> None:
        """Add MinMax operational policy config."""
        #must configure start/end time and min/max instances in json file
        template = jinja_env().get_template("clamp_MinMax_config.json.j2")
        return template.render(name=self.extract_operational_policy_name("MinMax"))

    def add_frequency_limiter(self, limit: int = 1) -> None:
        """Add frequency limiter config."""
        template = jinja_env().get_template("clamp_add_frequency.json.j2")
        return template.render(name=self.extract_operational_policy_name("FrequencyLimiter"),
                               LOOP_name=self.name,
                               limit=limit)

    def add_op_policy_config(self, func, **kwargs) -> None:
        """
        Add operational policy configuration.

        Add operation policy configuration using payload data.

        Args:
            func (function): policy configuration function in (add_drools_conf,
                                                               add_minmax_config,
                                                               add_frequency_limiter)

        """
        data = func(**kwargs)
        if not data:
            raise ParameterError("Payload data from configuration is None.")
        if self.operational_policies:
            self.operational_policies = self.operational_policies[:-1] + ","
            data = data[1:]
        self.operational_policies += data
        url = f"{self.base_url()}/loop/updateOperationalPolicies/{self.name}"
        self.send_message('POST',
                          'ADD operational policy config',
                          url,
                          data=self.operational_policies)

        self._logger.info(("Files for op policy config %s have been uploaded to loop's"
                           "Op policy"), self.name)

    def submit(self):
        """Submit policies to policy engine."""
        state = self.details["components"]["POLICY"]["componentState"]["stateName"]
        return state == "SENT_AND_DEPLOYED"

    def stop(self):
        """Undeploy Policies from policy engine."""
        state = self.details["components"]["POLICY"]["componentState"]["stateName"]
        return state == "SENT"

    def restart(self):
        """Redeploy policies to policy engine."""
        state = self.details["components"]["POLICY"]["componentState"]["stateName"]
        return state == "SENT_AND_DEPLOYED"

    def act_on_loop_policy(self, func) -> bool:
        """
        Act on loop's policy.

        Args:
            func (function): function of action to be done (submit, stop, restart)

        Returns:
            action state : failed or done

        """
        url = f"{self.base_url()}/loop/{func.__name__}/{self.name}"
        self.send_message('PUT',
                          f'{func.__name__} policy',
                          url)
        self.refresh_status()
        self.validate_details()
        return func()

    def deploy_microservice_to_dcae(self) -> bool:
        """
        Execute the deploy operation on the loop instance.

        Returns:
            loop deploy on DCAE status (True, False)

        """
        url = f"{self.base_url()}/loop/deploy/{self.name}"
        self.send_message('PUT',
                          'Deploy microservice to DCAE',
                          url)
        self.validate_details()
        state = self.details["components"]["DCAE"]["componentState"]["stateName"]
        failure = "MICROSERVICE_INSTALLATION_FAILED"
        success = "MICROSERVICE_INSTALLED_SUCCESSFULLY"
        while state not in (success, failure):
            self.refresh_status()
            self.validate_details()
            state = self.details["components"]["DCAE"]["componentState"]["stateName"]
        return state == success

    def undeploy_microservice_from_dcae(self) -> None:
        """Stop the deploy operation."""
        url = f"{self.base_url()}/loop/undeploy/{self.name}"
        self.send_message('PUT',
                          'Undeploy microservice from DCAE',
                          url)

    def delete(self) -> None:
        """Delete the loop instance."""
        self._logger.debug("Delete %s loop instance", self.name)
        url = "{}/loop/delete/{}".format(self.base_url(), self.name)
        self.send_message('PUT',
                          'Delete loop instance',
                          url)
