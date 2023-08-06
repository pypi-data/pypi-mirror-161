import json
import logging
from abc import ABC
from functools import lru_cache
from types import TracebackType
from typing import (
    Union, Any, Optional, NoReturn, Type, NamedTuple, OrderedDict
)

import aiohttp
import requests
from aiohttp import ClientResponse
from aiohttp import ClientResponseError
from aioretry import retry as aretry
from multidict import CIMultiDictProxy
from seqslab.auth.commands import BaseAuth
from seqslab.trs import __version__, API_HOSTNAME
from tenacity import retry, wait_fixed, stop_after_attempt
from yarl import URL

"""
Copyright (C) 2022, Atgenomix Incorporated.

All Rights Reserved.

This program is an unpublished copyrighted work which is proprietary to
Atgenomix Incorporated and contains confidential information that is not to
be reproduced or disclosed to any other person or entity without prior
written consent from Atgenomix, Inc. in each and every instance.

Unauthorized reproduction of this program as well as unauthorized
preparation of derivative works based upon the program or distribution of
copies by sale, rental, lease or lending are violations of federal copyright
laws and state trade secret laws, punishable by civil and criminal penalties.
"""


class BaseResource(ABC):
    logger = logging.getLogger()

    TOKENS_KEY = "tokens"
    TRS_BASE_URL = f"https://{API_HOSTNAME}/trs/{__version__}/"
    TRS_WORKSPACE_URL = f"{TRS_BASE_URL}service-info/workspaces/"
    TRS_RESOURCES_URL = f"{TRS_WORKSPACE_URL}{{name}}/resources/"
    TRS_CONTAINER_REGISTRY_URL = f"{TRS_WORKSPACE_URL}{{name}}/container-registries/"

    class Response(NamedTuple):
        status: int
        headers: CIMultiDictProxy[str]
        body: Any = None
        attrs: OrderedDict = {}

    def __init__(self, workspace):
        """
        :param workspace: resource group in Azure, or project in GCS
        """
        self._workspace = workspace
        self.session = aiohttp.ClientSession(raise_for_status=True)

    def __enter__(self) -> "BaseResource":
        return self

    def __exit__(self,
                 exc_type: Optional[Type[BaseException]],
                 exc_val: Optional[BaseException],
                 exc_tb: Optional[TracebackType],
                 ) -> None:
        pass

    @staticmethod
    def log(
        level: Any, response: Union[ClientResponse, ClientResponseError, dict],
        **kwargs
    ) -> NoReturn:
        msg = {"service": "cli",
               "category": "wes",
               "level": level,
               "user": BaseAuth.get_token()["attrs"]["user_id"]}
        msg.update(kwargs)
        if isinstance(response, ClientResponse):
            msg.update({"status": response.status,
                        "method": response.method,
                        "url": str(response.url)})
        elif isinstance(response, ClientResponseError):
            msg.update({"status": response.status,
                        "message": response.message,
                        "method": response.request_info.method,
                        "url": str(response.request_info.url)})
        else:
            assert isinstance(response, dict)
            msg.update({"status": response.get("status"),
                        "message": response.get("message"),
                        "method": response.get("method"),
                        "url": response.get("url")})
        BaseResource.logger.log(level, json.dumps(msg))

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True)
    @lru_cache(maxsize=16)
    def workspace(name) -> dict:
        token = BaseAuth.get_token().get("tokens").get("access")
        url = BaseResource.TRS_RESOURCES_URL.format(name=name)
        with requests.get(url,
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError()
            return response.json()

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True)
    @lru_cache(maxsize=16)
    def container_registry(name) -> dict:
        token = BaseAuth.get_token().get("tokens").get("access")
        with requests.get(BaseResource.TRS_CONTAINER_REGISTRY_URL.format(name=name),
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError('{"detail":"Workspace must be in SeqsLab supported Azure resource group.",'
                                         '"code":"internal_server_error"}')
            return response.json()

    @aretry(retry_policy="request_retry_policy")
    async def request(
        self, url: URL, method="GET", headers=None, *args, **kwargs
    ) -> Optional[Response]:
        """
        By default the response raises ClientResponseError when http error.
        Pass raise_for_status=False to disable and get tuple(status, text)
        return value.
        """
        assert url.scheme in ["http", "https"]

        headers = {} if headers is None else headers.copy()
        self.log(logging.DEBUG, self.auth_headers())
        if not headers.get("Authorization"):
            for _, (k, v) in enumerate(self.auth_headers().items()):
                headers.setdefault(k, v)
        if kwargs.get("accept"):
            headers.setdefault("Accept", kwargs.get("accept"))
        proxy = kwargs.get("proxy")
        data = None
        if kwargs.get("data", None):
            data = kwargs.get("data")
        async with self.session.request(method, str(url),
                                        headers=headers,
                                        proxy=proxy, data=data) as response:
            self.log(logging.INFO, response)
            if not response.ok:
                return self.Response(response.status,
                                     response.headers,
                                     await response.text())
            elif "application/json" in response.content_type:
                return self.Response(response.status,
                                     response.headers,
                                     await response.json())
            elif "text/plain" in response.content_type:
                return self.Response(response.status,
                                     response.headers,
                                     await response.text())
            return self.Response(response.status,
                                 response.headers)

    def auth_headers(self) -> dict:
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except Exception as e:
            self.log(logging.ERROR, e)
            raise Exception("Not Authenticated, Please run auth signin")
        return {"Authorization": f"Bearer {token}"}


