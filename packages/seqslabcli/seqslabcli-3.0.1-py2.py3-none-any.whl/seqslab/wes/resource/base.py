import json
import logging
from abc import ABC
from functools import lru_cache
from types import TracebackType
from typing import (Union, Any, Optional, NoReturn, Type, NamedTuple, OrderedDict)

import aiohttp
from aiohttp import FormData
import requests
import time
from multidict import CIMultiDictProxy

from yarl import URL
from aiohttp import ClientResponse
from aiohttp import ClientResponseError
from aioretry import retry as aretry
from tenacity import retry, wait_fixed, stop_after_attempt

from seqslab.auth.commands import BaseAuth
from seqslab.wes import __version__, API_HOSTNAME


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
    BLOB_SERVICE_URL = None
    WES_BASE_URL = f"https://{API_HOSTNAME}/wes/{__version__}/"
    WES_WORKSPACE_URL = f"{WES_BASE_URL}service-info/workspaces/"
    WES_RESOURCES_URL = f"{WES_WORKSPACE_URL}{{name}}/resources/"
    WES_RUNS_URL = f"{WES_BASE_URL}runs/"
    WES_RUNS_DRY_URL = f"{WES_BASE_URL}runs/dryrun/"
    WES_RUNS_FILE_URL = f"{WES_BASE_URL}runs/{{id}}/files/"
    WES_RUNS_STATUS_URL = f"{WES_BASE_URL}runs/{{id}}/status/"
    WES_RUNTIME_OPTIONS_URL = f"{WES_BASE_URL}runtime-options/{{name}}"

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
        url = BaseResource.WES_RESOURCES_URL.format(name=name)
        with requests.get(url, headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError()
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

    def get_run_status(self, run_id) -> dict:
        token = BaseAuth.get_token().get('tokens').get('access')
        with requests.get(url=f"{self.WES_RUNS_STATUS_URL.format(id=run_id)}/",
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError()
            return json.loads(response.content)

    def sync_run_jobs(self, data, headers, run_request_id, run_name, retries=5) -> requests.Response:
        try:
            if not headers.get("Authorization"):
                for _, (k, v) in enumerate(self.auth_headers().items()):
                    headers.setdefault(k, v)

            if run_request_id:
                if run_name:
                    url = f'{self.WES_RUNS_URL}?request_id={run_request_id}&run_name={run_name}'
                else:
                    url = f'{self.WES_RUNS_URL}?request_id={run_request_id}'
            else:
                if run_name:
                    url = f'{self.WES_RUNS_URL}?run_name={run_name}'
                else:
                    url = self.WES_RUNS_URL

            response = requests.post(
                url,
                data=data,
                headers=headers
            )
            if not response.ok:
                raise requests.HTTPError(response.content)

        except Exception as err:
            print(err)
            raise err

        return response

    def dry_run(self, data, headers, run_request_id, run_name) -> requests.Response:
        try:
            if not headers.get("Authorization"):
                for _, (k, v) in enumerate(self.auth_headers().items()):
                    headers.setdefault(k, v)

            if run_request_id:
                if run_name:
                    url = f'{self.WES_RUNS_DRY_URL}?request_id={run_request_id}&run_name={run_name}'
                else:
                    url = f'{self.WES_RUNS_DRY_URL}?request_id={run_request_id}'
            else:
                if run_name:
                    url = f'{self.WES_RUNS_DRY_URL}?run_name={run_name}'
                else:
                    url = self.WES_RUNS_DRY_URL

            response = requests.post(
                url,
                data=data,
                headers=headers
            )
            if response.status_code not in [requests.codes.created]:
                raise requests.HTTPError(response.content)
        except Exception as err:
            print(err)
            raise err

        return response

    def wes_files(self, run_id) -> requests.Response:
        try:
            token = BaseAuth.get_token().get('tokens').get('access')
            with requests.get(url=f"{self.WES_RUNS_FILE_URL.format(id=run_id)}/",
                              headers={"Authorization": f"Bearer {token}"}) as response:
                if response.status_code not in [requests.codes.ok]:
                    raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
        except Exception as err:
            print(err)
            raise err
        return response.json()

    def get_runtime_setting(self, runtime_name: str) -> dict:
        token = BaseAuth.get_token().get('tokens').get('access')
        with requests.get(url=f"{self.WES_RUNTIME_OPTIONS_URL.format(name=runtime_name)}/",
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.json()

    def get_run_id(self, run_id) -> dict:
        token = BaseAuth.get_token().get('tokens').get('access')
        with requests.get(url=f"{self.WES_RUNS_URL}{run_id}/",
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(response.content)
            return json.loads(response.content)
