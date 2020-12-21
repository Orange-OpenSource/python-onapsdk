# SPDX-License-Identifier: Apache-2.0
"""CDS Blueprintprocessor module."""

from onapsdk.utils.jinja import jinja_env

from .cds_element import CdsElement


class Blueprintprocessor(CdsElement):
    """Blueprintprocessor class."""

    @classmethod
    def bootstrap(cls,
                  load_model_type: bool = True,
                  load_resource_dictionary: bool = True,
                  load_cba: bool = True) -> None:
        """Bootstrap CDS blueprintprocessor.

        That action in needed to work with CDS. Can be done only once.

        Args:
            load_model_type (bool, optional): Datermines if model types should be loaded
                on bootstrap. Defaults to True.
            load_resource_dictionary (bool, optional): Determines if resource dictionaries
                should be loaded on bootstrap. Defaults to True.
            load_cba (bool, optional): Determines if cba files should be loaded on
                bootstrap. Defaults to True.

        """
        cls.send_message(
            "POST",
            "Bootstrap CDS blueprintprocessor",
            f"{cls._url}/api/v1/blueprint-model/bootstrap",
            data=jinja_env().get_template("cds_blueprintprocessor_bootstrap.json.j2").render(
                load_model_type=load_model_type,
                load_resource_dictionary=load_resource_dictionary,
                load_cba=load_cba
            ),
            auth=cls.auth,
            headers=cls.headers
        )
