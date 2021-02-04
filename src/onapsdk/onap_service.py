#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""ONAP Service module."""
from typing import Dict
from typing import Union
from typing import Any
from abc import ABC

import logging
import requests
import urllib3
from urllib3.util.retry import Retry
import simplejson.errors

from requests.adapters import HTTPAdapter
from requests import (  # pylint: disable=redefined-builtin
    HTTPError, RequestException, ConnectionError
)

from onapsdk.exceptions import (
    RequestError, APIError, ResourceNotFound, InvalidResponse,
    ConnectionFailed
)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class OnapService(ABC):
    """
    Mother Class of all ONAP services.

    An important attribute when inheriting from this class is `_jinja_env`.
    it allows to fetch simply jinja templates where they are.
    by default jinja engine will look for templates in `templates` directory of
    the package.
    See in Examples to see how to use.

    Attributes:
        server (str): nickname of the server we send the request. Used in logs
            strings. For example, 'SDC' is the nickame for SDC server.
        headers (Dict[str, str]): the headers dictionnary to use.
        proxy (Dict[str, str]): the proxy configuration if needed.

    """

    _logger: logging.Logger = logging.getLogger(__qualname__)
    server: str = None
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    proxy: Dict[str, str] = None

    def __init_subclass__(cls):
        """Subclass initialization.

        Add _logger property for any OnapService with it's class name as a logger name
        """
        super().__init_subclass__()
        cls._logger: logging.Logger = logging.getLogger(cls.__qualname__)

    def __init__(self) -> None:
        """Initialize the service."""
    @classmethod
    def send_message(cls, method: str, action: str, url: str,
                     **kwargs) -> Union[requests.Response, None]:
        """
        Send a message to an ONAP service.

        Args:
            method (str): which method to use (GET, POST, PUT, PATCH, ...)
            action (str): what action are we doing, used in logs strings.
            url (str): the url to use
            exception (Exception, optional): if an error occurs, raise the
                exception given instead of RequestError
            **kwargs: Arbitrary keyword arguments. any arguments used by
                requests can be used here.

        Raises:
            RequestError: if other exceptions weren't caught or didn't raise,
                            or if there was an ambiguous exception by a request
            ResourceNotFound: 404 returned
            APIError: returned an error code within 400 and 599, except 404
            ConnectionFailed: connection can't be established

        Returns:
            the request response if OK

        """
        cert = kwargs.pop('cert', None)
        basic_auth: Dict[str, str] = kwargs.pop('basic_auth', None)
        exception = kwargs.pop('exception', None)
        headers = kwargs.pop('headers', cls.headers)
        data = kwargs.get('data', None)
        try:
            # build the request with the requested method
            session = cls.__requests_retry_session()
            if cert:
                session.cert = cert
            OnapService._set_basic_auth_if_needed(basic_auth, session)

            cls._logger.debug("[%s][%s] sent header: %s", cls.server, action,
                              headers)
            cls._logger.debug("[%s][%s] url used: %s", cls.server, action, url)
            cls._logger.debug("[%s][%s] data sent: %s", cls.server, action,
                              data)

            response = session.request(method,
                                       url,
                                       headers=headers,
                                       verify=False,
                                       proxies=cls.proxy,
                                       **kwargs)

            cls._logger.info(
                "[%s][%s] response code: %s",
                cls.server, action,
                response.status_code if response is not None else "n/a")
            cls._logger.debug(
                "[%s][%s] response: %s",
                cls.server, action,
                response.text if response is not None else "n/a")

            response.raise_for_status()
            return response

        except HTTPError as cause:
            cls._logger.error("[%s][%s] API returned and error: %s",
                              cls.server, action, headers)

            msg = f'Code: {cause.response.status_code}. Info: {cause.response.text}.'

            if cause.response.status_code == 404:
                exc = ResourceNotFound(msg)
            else:
                exc = APIError(msg)

            raise exc from cause

        except ConnectionError as cause:
            cls._logger.error("[%s][%s] Failed to connect: %s", cls.server,
                              action, cause)

            msg = f"Can't connect to {url}."
            raise ConnectionFailed(msg) from cause

        except RequestException as cause:
            cls._logger.error("[%s][%s] Request failed: %s",
                              cls.server, action, cause)

        if not exception:
            msg = f"Ambiguous error while requesting {url}."
            raise RequestError(msg)

        raise exception

    @classmethod
    def _set_basic_auth_if_needed(cls, basic_auth, session):
        if basic_auth:
            session.auth = (basic_auth.get('username'),
                            basic_auth.get('password'))

    @classmethod
    def send_message_json(cls, method: str, action: str, url: str,
                          **kwargs) -> Dict[Any, Any]:
        """
        Send a message to an ONAP service and parse the response as JSON.

        Args:
            method (str): which method to use (GET, POST, PUT, PATCH, ...)
            action (str): what action are we doing, used in logs strings.
            url (str): the url to use
            exception (Exception, optional): if an error occurs, raise the
                exception given
            **kwargs: Arbitrary keyword arguments. any arguments used by
                requests can be used here.

        Raises:
            InvalidResponse: if JSON coudn't be decoded
            RequestError: if other exceptions weren't caught or didn't raise
            APIError/ResourceNotFound: send_message() got an HTTP error code
            ConnectionFailed: connection can't be established
            RequestError: send_message() raised an ambiguous exception


        Returns:
            the response body in dict format if OK

        """
        exception = kwargs.get('exception', None)
        data = kwargs.get('data', None)
        try:

            cls._logger.debug("[%s][%s] sent header: %s", cls.server, action,
                              cls.headers)
            cls._logger.debug("[%s][%s] url used: %s", cls.server, action, url)
            cls._logger.debug("[%s][%s] data sent: %s", cls.server, action,
                              data)

            response = cls.send_message(method, action, url, **kwargs)

            if response:
                return response.json()

        except simplejson.errors.JSONDecodeError as cause:
            cls._logger.error("[%s][%s]Failed to decode JSON: %s", cls.server,
                              action, cause)
            raise InvalidResponse from cause

        except RequestError as exc:
            cls._logger.error("[%s][%s] request failed: %s",
                              cls.server, action, exc)
            if not exception:
                exception = exc

        raise exception

    @staticmethod
    def __requests_retry_session(retries: int = 10,
                                 backoff_factor: float = 0.3,
                                 session: requests.Session = None
                                 ) -> requests.Session:
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

    @staticmethod
    def set_proxy(proxy: Dict[str, str]) -> None:
        """
        Set the proxy for Onap Services rest calls.

        Args:
            proxy (Dict[str, str]): the proxy configuration

        Examples:
            >>> OnapService.set_proxy({
            ...     'http': 'socks5h://127.0.0.1:8082',
            ...     'https': 'socks5h://127.0.0.1:8082'})

        """
        OnapService.proxy = proxy
