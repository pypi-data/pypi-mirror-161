import json
import logging
import os
from abc import abstractmethod
from functools import lru_cache
from types import TracebackType
from typing import (
    Union, Any, List, Optional, NamedTuple, NoReturn, OrderedDict, Type
)

import aiofiles
import aiohttp
import requests

from yarl import URL
from hashlib import md5
from base64 import b64encode
from aiohttp import ClientResponse
from aiohttp import ClientConnectionError, ClientResponseError, ServerTimeoutError
from aioretry import retry as aretry
from aioretry import RetryInfo, RetryPolicyStrategy
from multidict import CIMultiDictProxy
from tenacity import retry, wait_fixed, stop_after_attempt

from seqslab.auth.commands import BaseAuth
from seqslab.drs import __version__, API_HOSTNAME

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


class BaseBlob:
    logger = logging.getLogger()

    TOKENS_KEY = "tokens"
    BLOB_SERVICE_URL = None
    DRS_WORKSPACE_URL = f"https://{API_HOSTNAME}/ga4gh/drs/{__version__}/service-info/workspaces/"
    DRS_RESOURCES_URL = f"{DRS_WORKSPACE_URL}{{name}}/resources/"
    DRS_SAS_URL = f"https://{API_HOSTNAME}/ga4gh/drs/{__version__}/objects/upload/"
    DRS_REFRESH_SAS_URL = f"{DRS_SAS_URL}refresh/"
    DRS_DOWNLOAD_URL = f"https://{{API_HOSTNAME}}/ga4gh/drs/{__version__}/objects/{{drs_id}}/download/"

    def __init__(self, workspace):
        """
        :param workspace: resource group in Azure, or project in GCS
        """
        self.session = aiohttp.ClientSession(raise_for_status=True)
        self._workspace = workspace

    async def __aenter__(self) -> "BaseBlob":
        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException],
            exc_tb: Optional[TracebackType],
    ) -> None:
        await self.close()

    async def close(self):
        await self.session.close()

    @staticmethod
    def log(
            level: Any, response: Union[ClientResponse, ClientResponseError, dict],
            **kwargs
    ) -> NoReturn:
        msg = {"service": "cli",
               "category": "drs",
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
            assert isinstance(response, dict), f'Assertion Error{response}'
            msg.update({"status": response.get("status"),
                        "message": response.get("message"),
                        "method": response.get("method"),
                        "url": response.get("url")})
        BaseBlob.logger.log(level, json.dumps(msg))

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=False)
    def workspaces() -> dict:
        token = BaseAuth.get_token().get("tokens").get("access")
        with requests.get(BaseBlob.DRS_WORKSPACE_URL,
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError()
            return response.json()

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(5), reraise=True)
    @lru_cache(maxsize=16)
    def workspace(name) -> dict:
        token = BaseAuth.get_token().get("tokens").get("access")
        with requests.get(BaseBlob.DRS_RESOURCES_URL.format(name=name),
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError()
            return response.json()

    def request_retry_policy(
            self, info: RetryInfo
    ) -> RetryPolicyStrategy:
        if isinstance(info.exception, ClientResponseError):
            if info.exception.status in [requests.codes.forbidden]:
                # invalidate cache to get new access token, retry immediately
                # self.workspace.cache_clear()
                return info.fails > 1, 0
            elif info.exception.status in [requests.codes.server_error,
                                           requests.codes.service_unavailable]:
                return info.fails > 1, (info.fails - 1) % 3 * 0.1
        elif isinstance(info.exception, (ClientConnectionError, ServerTimeoutError)):
            return info.fails > 3, (info.fails - 1) % 3 * 0.1
        # otherwise, we don't retry
        return True, 0

    class Response(NamedTuple):
        status: int
        headers: CIMultiDictProxy[str]
        body: Any = None
        attrs: OrderedDict = {}

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

        if kwargs.get("accept"):
            headers.setdefault("Accept", kwargs.get("accept"))
        proxy = kwargs.get("proxy")
        async with self.session.request(method, str(url),
                                        data=kwargs.get("data", None),
                                        json=kwargs.get("json", None),
                                        headers=headers,
                                        proxy=proxy) as response:
            self.log(logging.INFO, response)
            if not response.ok:
                return self.Response(response.status,
                                     response.headers,
                                     await response.text())
            if kwargs.get("fileobj"):
                fd = kwargs.get("fileobj")
                size = kwargs.get("chunk_size", 64 * 1024 * 1024)
                cs = md5() if kwargs.get("md5_check", False) else None
                while True:
                    chunk = await response.content.read(size)
                    if not chunk:
                        break
                    os.write(fd, chunk)
                    if cs:
                        cs.update(chunk)
                if cs:
                    content_md5 = b64encode(cs.digest()).decode()
                    return self.Response(response.status,
                                         response.headers,
                                         None,
                                         {"x-content-md5": content_md5})
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
            data = self.workspace(self._workspace)
            tokens = data["tokens"][self.TOKENS_KEY]
            return {"Authorization": f"Bearer {tokens}"}
        except Exception:
            return {}

    def blob_service_url(self, uri, **kwargs) -> URL:
        return URL(self.BLOB_SERVICE_URL)

    @abstractmethod
    async def mkdirs(self, uri, permission=0o766, *args, **kwargs) -> Any:
        msg = '{cls}.mkdirs() must be implemented.'
        raise NotImplementedError(msg.format(
            cls=self.__class__.__name__
        ))

    async def delete(self, uri: URL, *args, **kwargs) -> bool:
        try:
            await self.request(uri, "DELETE",
                               *args, **kwargs)
            return True
        except ClientResponseError as err:
            self.log(logging.ERROR, err)
            return False

    @abstractmethod
    async def rmdir(self, uri: URL, *args, **kwargs) -> Any:
        msg = '{cls}.rmdir() must be implemented.'
        raise NotImplementedError(msg.format(
            cls=self.__class__.__name__
        ))

    @abstractmethod
    async def content(
            self, uri: URL, recursive=False, *args, **kwargs
    ) -> Optional[OrderedDict]:
        # {"directoryCount": 0,
        #  "fileCount": 0,
        #  "length": 0,
        #  "quota": 0,
        #  "spaceConsumed": 0,
        #  "spaceQuota": 0,
        #  "paths": []}
        msg = '{cls}.content() must be implemented.'
        raise NotImplementedError(msg.format(
            cls=self.__class__.__name__
        ))

    async def files(
            self, uri: URL, *args, **kwargs
    ) -> Union[List[str], OrderedDict]:
        r = await self.content(uri, *args, **kwargs)
        if not r: return []
        return [p["name"] for p in r["paths"]
                if not p.get("isDirectory", None)
                and not p.get("name").split("/")[-1].startswith(".")]

    async def directories(
            self, uri: URL, *args, **kwargs
    ) -> Union[List[str], OrderedDict]:
        r = await self.content(uri, *args, **kwargs)
        if not r: return []
        return [p["name"] for p in r["paths"]
                if p.get("isDirectory", None)]

    @abstractmethod
    async def create(
            self, uri: URL, permission=0o766, *args, **kwargs
    ) -> bool:
        """
        Create a new file for uploading data.
        """
        msg = '{cls}.create() must be implemented.'
        raise NotImplementedError(msg.format(
            cls=self.__class__.__name__
        ))

    async def upload(
            self, uri: URL, file: str, chunk_size: int, *args, **kwargs
    ) -> int:
        async def data_reader(path=None):
            async with aiofiles.open(path, "rb") as f:
                chunk = await f.read(chunk_size)
                while chunk:
                    yield chunk
                    chunk = await f.read(chunk_size)

        try:
            await self.request(uri, "PUT", data=data_reader(path=file),
                               *args, **kwargs)
            return os.stat(file).st_size
        except ClientResponseError as err:
            self.log(logging.ERROR, err)
            return 0

    async def download(
            self, uri: URL, file: str, chunk_size=64 * 1024 * 1024, *args, **kwargs
    ) -> Any:
        async with aiofiles.open(file, mode="wb") as fileobj:
            return await self.request(uri,
                                      fileobj=fileobj,
                                      chunk_size=chunk_size,
                                      *args, **kwargs)

    @abstractmethod
    async def status(
            self, uri: URL, *args, **kwargs
    ) -> Optional[OrderedDict]:
        msg = '{cls}.status() must be implemented.'
        raise NotImplementedError(msg.format(
            cls=self.__class__.__name__
        ))

    @abstractmethod
    def set_access_tier(self, uri: URL, tier, *args, **kwargs) -> Any:
        msg = '{cls}.set_access_tier() must be implemented.'
        raise NotImplementedError(msg.format(
            cls=self.__class__.__name__
        ))
