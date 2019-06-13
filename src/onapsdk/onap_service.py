#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""ONAP Service module."""
from typing import Dict
from typing import Union
from typing import Any

import logging
import requests
from requests.adapters import HTTPAdapter
import urllib3
from urllib3.util.retry import Retry
import simplejson.errors
from jinja2 import Environment, PackageLoader, select_autoescape

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class OnapService():
    """
    Mother Class of all ONAP services.

    An important attribute when inheriting from this class is `_jinja_env`.
    it allows to fetch simply jinja templates where they are.
    by default jinja engine will look for templates in `templates` directory of
    the package.
    See in Examples to see how to use

    Class Attributes:
        server (str): nickname of the server we send the request.
                      used in logs strings. For example,'SDC' is the nickame
                      for SDC server...
        header (Dict[str, str]): the header dictionnary to use
        proxy (Dict[str, str]): the proxy configuration if needed

    Examples:
        >>> onapService = OnapService()
        >>> template = onapService._jinja_env.get_template('vendor_create.json.j2')
        >>> data = template.render(name="my_name")

    """

    __logger: logging.Logger = logging.getLogger(__name__)
    server: str = None
    header: Dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    proxy: Dict[str, str] = None

    def __init__(self) -> None:
        """Initialize the service."""
        # _jinja_env allow to fetch simply jinja templates where they are.
        # by default jinja engine will look for templates in `templates`
        # directory of the package.
        # so to load a template, you just have to do:
        #
        # ```python
        # template = self._jinja_env.get_template('my_template.json.j2')
        # data = template.render(template_var="a_value", another_var=self.var)
        # ```
        #
        # see Vendor.create() for real use
        self._jinja_env = Environment(
            autoescape=select_autoescape(['html', 'htm', 'xml']),
            loader=PackageLoader('onapsdk'))

    @classmethod
    def send_message(cls, method: str, action: str, url: str,
                     **kwargs) -> Union[requests.Request, None]:
        """
        Send a message to an ONAP service.

        Args:
            method (str): which method to use (GET, POST, PUT, PATCH, ...)
            action (str): what action are we doing, used in logs strings.
            url (str): the url to use
            exception (Exception, optional): if an error occurs, raise the
                exception given
            **kwargs: Arbitrary keyword arguments. any arguments used by request
                can be used here.

        Raises:
            exception (Exception): raise the Exception given in args (if given)

        Returns:
            the request response if OK or None if an error occured

        """
        exception = kwargs.pop('exception', None)
        data = kwargs.get('data', None)
        try:
            # build the request with the requested method
            session = cls.__requests_retry_session()
            response = session.request(method, url, headers=cls.header,
                                       verify=False, proxies=cls.proxy,
                                       **kwargs)

            response.raise_for_status()
            cls.__logger.info("[%s][%s] response code: %s", cls.server,
                              action, response.status_code)
            cls.__logger.debug("[%s][%s] sent header: %s",
                               cls.server, action, cls.header)
            cls.__logger.debug("[%s][%s] url used: %s", cls.server, action, url)
            cls.__logger.debug("[%s][%s] data sent: %s", cls.server, action,
                               data)
            cls.__logger.debug("[%s][%s] response: %s", cls.server, action,
                               response.text)
            return response
        except requests.HTTPError:
            cls.__logger.error(
                "[%s][%s] response code: %s", cls.server, action,
                response.status_code)
            cls.__logger.error("[%s][%s] response: %s", cls.server, action,
                               response.text)
        except requests.RequestException as err:
            cls.__logger.error("[%s][%s] Failed to perform: %s", cls.server,
                               action, err)
        # We are passing here only if we catched an error
        cls.__logger.error("[%s][%s] sent header: %s", cls.server, action,
                           cls.header)
        cls.__logger.error("[%s][%s] url used: %s", cls.server, action, url)
        cls.__logger.error("[%s][%s] data sent: %s", cls.server, action, data)
        # if specific exception predefined
        # for the given service, raise it
        if exception:
            raise exception
        return None

    @classmethod
    def send_message_json(cls, method: str, action: str, url: str,
                          **kwargs) -> Union[Dict[Any, Any], None]:
        """
        Send a message to an ONAP service and parse the response as JSON.

        Args:
            method (str): which method to use (GET, POST, PUT, PATCH, ...)
            action (str): what action are we doing, used in logs strings.
            url (str): the url to use
            exception (Exception, optional): if an error occurs, raise the
                exception given
            **kwargs: Arbitrary keyword arguments. any arguments used by request
                can be used here.

        Raises:
            exception (Exception): raise the Exception given in args (if given)

        Returns:
            the response body in dict format if OK or {}

        """
        exception = kwargs.get('exception', None)
        data = kwargs.get('data', None)
        try:
            response = cls.send_message(method, action, url, **kwargs)
            if response:
                return response.json()
        except simplejson.errors.JSONDecodeError as err:
            cls.__logger.error("[%s][%s]Failed to decode JSON: %s",
                               cls.server, action, err)
            cls.__logger.error("[%s][%s] sent header: %s", cls.server, action,
                               cls.header)
            cls.__logger.error("[%s][%s] url used: %s", cls.server, action, url)
            cls.__logger.error("[%s][%s] data sent: %s", cls.server, action,
                               data)
            if exception:
                raise exception
        return {}

    @staticmethod
    def __requests_retry_session(
            retries: int = 10,
            backoff_factor: float = 0.3,
            session: requests.Session = None) -> requests.Session:
        """
        Create a request Session with retries.

        Args:
            retries (int, optional): number of retries. Defaults to 10.
            backoff_factor (float, optional): backoff_factor. Defaults to 0.3.
            session (requests.Session, optional): an existing session to
                enhance. Defaults to None.

        Returns:
            requests.Session: the session with retries set

        """
        session = session or requests.Session()
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
            backoff_factor=backoff_factor,
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    @classmethod
    def set_proxy(cls, proxy: Dict[str, str]) -> None:
        """
        Set the proxy for Onap Services rest calls.

        Args:
            proxy (Dict[str, str]): the proxy configuration

        Examples:
            >>> OnapService.set_proxy({
            ...     'http': 'socks5h://127.0.0.1:8082',
            ...     'https': 'socks5h://127.0.0.1:8082'})

        """
        cls.proxy = proxy
