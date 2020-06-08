#!/usr/bin/python
#
# This program and the accompanying materials
# are made available under the terms of the Apache License, Version 2.0
# which accompanies this distribution, and is available at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
"""Utils class."""
import json
import string
import random
from typing import Dict

def get_parameter_from_yaml(parameter, config_file):
    """
    Get the value of a given parameter in file.yaml.

    Parameter must be given in string format with dots
    Example: general.openstack.image_name
    :param config_file: yaml file of configuration formtatted as string
    :return: the value of the parameter
    """
    # with open(config_file) as my_file
    #     file_yaml = yaml.safe_load(my_file)
    # my_file.close()
    # value = file_yaml
    value = json.loads(config_file)
    # Ugly fix as workaround for the .. within the params in the yaml file
    ugly_param = parameter.replace("..", "##")
    for element in ugly_param.split("."):
        value = value.get(element.replace("##", ".."))
        if value is None:
            raise ValueError("Parameter %s not defined" % parameter)

    return value

def get_vf_list_from_tosca_file(model):
    """
    Get the list of Vfs of a VNF based on the tosca file.

    :param model: the model retrieved from the tosca file at Vnf instantiation

    :return: the list of Vfs
    """
    newlist = []
    node_list = get_parameter_from_yaml(
        "topology_template.node_templates", model)

    for node in node_list:
        value = get_parameter_from_yaml(
            "topology_template.node_templates." + node + ".type",
            model)
        if "org.openecomp.resource.vf" in value:
            print(node, value)
            if node not in newlist:
                search_value = str(node).split(" ")[0]
                newlist.append(search_value)
    return newlist

def get_modules_list_from_tosca_file(model: str) -> Dict:
    """Get the list of modules from tosca file.

    Modules are stored on topology_template.groups TOSCA file section.

    :param model: the model retrieved from the tosca file at Vnf instantiation
    :return: the list of modules
    :raises:
        ValueError: no modules in Tosca file
    """
    return get_parameter_from_yaml(
        "topology_template.groups", model
    )

def random_string_generator(size=6,
                            chars=string.ascii_uppercase + string.digits):
    """
    Get a random String for VNF.

    6 alphanumerical char for CI (to get single instances)
    :return: a random sequence of 6 characters
    """
    return ''.join(random.choice(chars) for _ in range(size))
