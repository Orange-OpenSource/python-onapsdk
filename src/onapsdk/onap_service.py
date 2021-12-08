#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: Apache-2.0
"""ONAP Service module."""
from abc import ABC
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Iterator, List, Optional, Union

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
    ConnectionFailed, NoGuiError
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
        permanent_headers (Optional[Dict[str, str]]): optional dictionary of
            headers which could be set by the user and which are **always**
            added into sended request. Unlike the `headers`, which could be
            overrided on `send_message` call these headers are constant.

    """

    @dataclass
    class PermanentHeadersCollection:
        """Collection to store permanent headers."""

        ph_dict: Dict[str, Any] = field(default_factory=dict)
        ph_call: List[Callable] = field(default_factory=list)

        def __iter__(self) -> Iterator[Dict[str, any]]:
            """Iterate through the headers.

            For dictionary based headers just return the dict and
            for the callables iterate through the list of them,
            call them and yield the result.
            """
            yield self.ph_dict
            for ph_call in self.ph_call:
                yield ph_call()

    _logger: logging.Logger = logging.getLogger(__qualname__)
    server: str = None
    headers: Dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    proxy: Dict[str, str] = None
    permanent_headers: PermanentHeadersCollection = PermanentHeadersCollection()

    def __init_subclass__(cls):
        """Subclass initialization.

        Add _logger property for any OnapService with it's class name as a logger name
        """
        super().__init_subclass__()
        cls._logger: logging.Logger = logging.getLogger(cls.__qualname__)

    def __init__(self) -> None:
        """Initialize the service."""

    @classmethod
    def send_message(cls, method: str, action: str, url: str,  # pylint: disable=too-many-locals
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
        headers = kwargs.pop('headers', cls.headers).copy()
        if OnapService.permanent_headers:
            for header in OnapService.permanent_headers:
                headers.update(header)
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
                response.text if (response is not None and
                                  response.headers.get("Content-Type", "") == \
                                      "application/json") else "n/a")

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
        try:

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

    @staticmethod
    def set_header(header: Optional[Union[Dict[str, Any], Callable]] = None) -> None:
        """Set the header which will be always send on request.

        The header can be:
            * dictionary - will be used same dictionary for each request
            * callable - a method which is going to be called every time on request
              creation. Could be useful if you need to connect with ONAP through some API
              gateway and you need to take care about authentication. The callable shouldn't
              require any parameters
            * None - reset headers

        Args:
            header (Optional[Union[Dict[str, Any], Callable]]): header to set. Defaults to None

        """
        if not header:
            OnapService._logger.debug("Reset headers")
            OnapService.permanent_headers = OnapService.PermanentHeadersCollection()
            return
        if callable(header):
            OnapService.permanent_headers.ph_call.append(header)
        else:
            OnapService.permanent_headers.ph_dict.update(header)
        OnapService._logger.debug("Set permanent header %s", header)

    @classmethod
    def get_guis(cls):
        """Return the list of GUI and its status."""
        raise NoGuiError
