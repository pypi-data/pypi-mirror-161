import logging
import os
import re
import asyncio

import aiofiles
from numba import njit
from numba.typed import List

from yarl import URL
from typing import Optional, Literal, Any, OrderedDict, NoReturn
from base64 import b64encode
from aiofiles.os import sendfile
from aiohttp import ClientResponseError

from .base import BaseBlob
import datetime
from seqslab.auth.commands import BaseAuth
import requests
import json
from functools import lru_cache
import arrow
from xml.etree import ElementTree
from io import BytesIO
from hashlib import md5
from seqslab.drs import API_HOSTNAME
import shutil

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


class BlobStorage(BaseBlob):
    """
    Azure Blob service stores text and binary data as objects in the cloud.
    The Blob service offers the following three resources:
    the storage account, containers, and blobs.
    """

    TOKENS_KEY = "Microsoft.Storage/storageAccounts"
    BLOB_SERVICE_URL = "https://{account}.blob.core.windows.net"

    def __init__(self, workspace):
        self.buffer = {}
        super().__init__(workspace)

    @lru_cache(maxsize=16)
    def refresh_token(self, uri: URL, **kwargs):
        token = BaseAuth.get_token().get("tokens").get("access")
        query_param = uri.human_repr()
        with requests.get(BaseBlob.DRS_REFRESH_SAS_URL,
                          headers={"Authorization": f"Bearer {token}"},
                          params={"upload_url": query_param}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.text}")
            return json.loads(response.text)

    def refresh_service_url(self, uri: URL, **kwargs) -> URL:
        """
        :param uri: blob uri, ex: https://seqslabapi97e51storage.blob.core.windows.net/path/...
        :return: complete blob endpoint url with SAS token, ex: https://host/container/path/...?
        st=2021-09-23T02%3A17%3A16Z&se=2021-09-23T03%3A17%3A16Z....
        """
        try:
            data = self.refresh_token(uri.with_query(""))
            sas_token = data["headers"]["Authorization"]
            end_time = URL(sas_token).human_repr().split('&')[1].split("=")[1]
            if arrow.utcnow() > arrow.get(end_time):
                self.refresh_token.cache_clear()
                data = self.refresh_token(uri.with_query(""))
                sas_token = data["headers"]["Authorization"]
            return URL(uri).with_query(sas_token)
        except LookupError as error:
            raise LookupError(repr(error))

    def auth_headers(self):
        headers = super().auth_headers()
        headers.update({"x-ms-version": "2020-08-04"})
        return headers

    @lru_cache(maxsize=16)
    def get_token(self, path: str) -> dict:
        token = BaseAuth.get_token().get("tokens").get("access")
        workspace = self._workspace
        url = BaseBlob.DRS_SAS_URL.format(name=workspace)
        with requests.get(url.format(name=workspace),
                          headers={"Authorization": f"Bearer {token}"},
                          params={"name": workspace,
                                  "path": path}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.text}")
            return response.json()

    def blob_service_url(self, uri: URL, **kwargs) -> URL:
        """
        :param uri: dst uri, ex: abfss://hostname/path/to/folder or file...
        :return: complete blob endpoint url, ex: https://host/container/path/ or with_query SAS token...
        """

        if isinstance(self, FileSystemStorage):
            data = self.workspace(name=self._workspace)
            url = self.BLOB_SERVICE_URL.format(account=data["resources"][0]["name"])
            return URL(url).with_path(os.path.join(uri.host.strip("/"), uri.path.strip("/")))

        src = kwargs.get("src")
        if src:
            # force the src variable‘s basename is same as dst argumet
            if os.path.basename(src) != os.path.basename(str(uri)):
                src = os.path.join(os.path.dirname(src), os.path.basename(str(uri)))

            if uri.scheme:
                parts = uri.parts
                if uri.scheme in ['abfss', 'abfs'] and uri.host.endswith('.dfs.core.windows.net'):
                    if len(parts) < 3 or not parts[1] == 'drs' or not parts[2].startswith('usr_'):
                        raise ValueError('Enter a valid dst in abfss://container@storageaccount.dfs.core.windows.net'
                                         '/path/')
                    else:
                        return self.refresh_service_url(uri)

                elif uri.scheme in ['https', 'http'] and uri.host.endswith('.blob.core.windows.net'):
                    if len(parts) < 3 or not parts[1] == 'drs' or not parts[2].startswith('usr_'):
                        raise ValueError('Enter a valid dst in https://storageaccount.blob.core.windows.net/container/'
                                         '/path/')
                    else:
                        return self.refresh_service_url(uri)

                else:
                    raise ValueError('Enter a valid dst according to the choosing backend.')

            name = os.path.commonprefix([str(uri)[::-1], src[::-1]])[::-1]
            if not name.startswith("/") and len(name.split("/")) != 1:
                name = os.path.join(*name.split("/")[1:]).strip("/")
            else:
                name = name.strip("/")
            path = uri.path.replace(name, "")
            if path == "/":
                path = None
            data = self.get_token(path)
            sas_token = data["headers"]["Authorization"]
            end_time = URL(sas_token).human_repr().split('&')[1].split("=")[1]
            if arrow.utcnow() > arrow.get(end_time):
                self.get_token.cache_clear()
                data = self.get_token(path)
            return URL(data["url"]).join(URL(name)).update_query(data["headers"]["Authorization"])
        return uri.with_query(kwargs.get('token'))

    @staticmethod
    @njit(nogil=True)
    def _sum_send(results):
        sent = 0
        for res in results:
            if res == 0: break
            sent += res
        return sent

    async def set_access_tier(
            self, uri: URL, tier: Literal["hot", "cool", "archive"], *args, **kwargs
    ) -> Any:
        files = await self.files(uri, *args, **kwargs)
        for f in files:
            url = self.blob_service_url(uri.with_path(f)).update_query("comp=tier")
            try:
                await self.request(url, "PUT",
                                   headers={"x-ms-access-tier": tier},
                                   *args, **kwargs)
            except ClientResponseError as err:
                self.log(logging.ERROR, err)

    @staticmethod
    def _url_transform(url: URL) -> URL:
        """
        In Azure backend: we store access url with 'abfs or abfss' scheme in mysql database
        https or http -> abfss or abfs
        """
        if url.host.endswith('blob.core.windows.net'):
            host_path = f'{url.parts[1]}@{url.host.split(".")[0]}.dfs.core.windows.net/{"/".join(url.parts[2:])}'
            if url.scheme == 'http':
                url = f'abfs://{host_path}'
            elif url.scheme == 'https':
                url = f'abfss://{host_path}'
        return URL(url)

    async def upload(
            self, uri: URL, file: str,
            chunk_size: int = 16 * 1024 * 1024,
            max_concurrency: int = 0,
            md5_check: bool = True, *args,
            **kwargs
    ) -> dict:
        """
        Asynchronous single file uploading
        :return the number of bytes sent.
        """
        file_size = os.stat(file).st_size
        uri = self.blob_service_url(uri=uri, src=file)
        position = 0
        index = 0
        block_id_head = '<?xml version="1.0" encoding="utf-8"?> <BlockList>'
        typed_results = List()
        with open(file, 'rb') as f:
            while position < file_size:
                tasks = []
                size = min(max_concurrency * chunk_size, file_size - position)
                end_chunk = size + position
                for pos in range(position, end_chunk, chunk_size):
                    index += 1
                    data = f.read(chunk_size)
                    base64_message = b64encode(md5(data).hexdigest().encode()).decode('ascii')
                    block_id_head += f'<Latest>{base64_message}</Latest>'
                    root = self.get_block_list(uri=uri)
                    block_list = [child.find('Name').text for child in root.iter('Block')] if root else []
                    block_size_list = [child.find('Size').text for child in root.iter('Block')] if root else []
                    if base64_message in block_list:
                        block_size = int(block_size_list[block_list.index(base64_message)])
                        if chunk_size == block_size or (end_chunk - pos) == block_size:
                            typed_results.append(block_size)
                            continue
                    tasks.append(self.put_block(uri=uri, data=data, position=pos, size=chunk_size,
                                                base64_message=base64_message, md5_check=md5_check, **kwargs))
                results = await asyncio.gather(*tasks, return_exceptions=True)
                [typed_results.append(x) for x in results if isinstance(x, int)]
                sent = self._sum_send(typed_results)
                typed_results.clear()

                if sent != size:
                    # request fail and return
                    break

                position += sent

        block_id = block_id_head + '</BlockList>'
        await self.put_blocklist(uri, block_id, **kwargs)
        created_time = datetime.datetime.utcnow()
        workspace = self.workspace(name=self._workspace)

        # end while
        return {
            "position": position,
            "dst": [str(self._url_transform(uri.with_query("")))],
            "created_time": datetime.datetime.strftime(created_time, "%Y-%m-%dT%H:%M:%S.%f"),
            "region": workspace['location'],
            "access_methods_type": [self._url_transform(uri.with_query("")).scheme]
        }

    @lru_cache(maxsize=16)
    def get_block_list(self, uri: URL) -> iter:
        date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        query_param = {
            "comp": "blocklist",
            "blocklisttype": "all"
        }
        url = uri.update_query(query_param)
        headers = {
            'x-ms-version': "2019-12-12",
            "x-ms-date": date,
        }
        get_block_list = requests.get(
            url=str(url),
            headers=headers,
        )
        if get_block_list.status_code == 200:
            return ElementTree.fromstring(get_block_list.text)

    async def put_block(self, uri: URL, data: open, position: int, size: int,
                        base64_message: str, md5_check: bool, *args, **kwargs) -> int:
        url = uri.update_query(f"comp=block&blockid={base64_message}")
        date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {'x-ms-version': "2019-12-12", "x-ms-date": date, "Content-Type": "application/octet-stream"}
        length = len(data)
        headers["Content-Length"] = str(length)
        if md5_check:
            headers["Content-MD5"] = b64encode(md5(data).digest()).decode()
        retry = 5
        while retry:
            try:
                buffer = BytesIO(data)
                buffer.seek(0)
                await self.request(url, "PUT",
                                   headers=headers, data=buffer,
                                   *args, **kwargs)
                buffer.close()
                return length
            except ClientResponseError as err:
                retry -= 1
                uri = self.refresh_service_url(uri)
                url = uri.update_query(f"comp=block&blockid={base64_message}")
                if retry == 0:
                    self.log(logging.ERROR, err)
                    return 0
                pass
            except Exception as err:
                retry -= 1
                if retry == 0:
                    self.log(logging.ERROR, err)
                    return 0
                pass

    async def put_blocklist(
            self, uri: URL, block_id: str, *args, **kwargs
    ) -> NoReturn:
        date = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        url = uri.update_query(f"comp=blocklist")
        retry = 5
        while retry:
            retry -= 1
            try:
                resp = await self.request(url, "PUT",
                                          headers={
                                              'x-ms-version': "2019-12-12",
                                              "x-ms-date": date,
                                              "Content-Length": str(len(block_id))
                                          },
                                          data=block_id, *args, **kwargs)
            except ClientResponseError as err:
                uri = self.refresh_service_url(uri)
                url = uri.update_query(f"comp=blocklist")
                if retry == 0:
                    self.log(logging.ERROR, err)
                    return 0
                pass
            except Exception as err:
                if retry == 0:
                    self.log(logging.ERROR, err)
                    return 0
                pass

    @lru_cache(maxsize=16)
    async def expand_blob(self, drs_id, **kwargs) -> List[dict] or requests.HTTPError:
        token = BaseAuth.get_token().get("tokens").get("access")
        with requests.get(
                BaseBlob.DRS_DOWNLOAD_URL.format(
                    API_HOSTNAME=kwargs.get('self_uri_host', API_HOSTNAME), drs_id=drs_id),
                headers={"Authorization": f"Bearer {token}"},
                params={'name': kwargs.get('workspace')}
        ) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{json.loads(response.text)}")
            return json.loads(response.text)

    async def download(
            self, uri: URL, file: str,
            chunk_size=64 * 1024 * 1024,
            max_concurrency: int = 1,
            md5_check: bool = True,
            overwrite: bool = False, *args,
            **kwargs
    ) -> dict:
        url = self.blob_service_url(uri=uri, token=kwargs.get('token'))
        file_size = kwargs.get('size')
        temp_file = f"{file}.{str(md5(str(uri).encode()).hexdigest())}"
        typed_results = List()
        workspace = self.workspace(name=self._workspace)
        if overwrite:
            if os.path.exists(file):
                os.remove(file)
            elif os.path.exists(temp_file):
                os.remove(temp_file)
            start = 0
        else:
            if os.path.exists(file):
                exist_size = os.stat(file).st_size
                return {
                    "position": exist_size,
                    "dst": file,
                    "created_time": datetime.datetime.strftime(datetime.datetime.utcnow(), "%Y-%m-%dT%H:%M:%S.%f"),
                    "region": workspace['location'],
                    "access_methods_type": workspace['resources'][0]['type'],
                    "exception": ValueError(
                        'Make sure the the file needs to be overwritten or rename the dst name.'
                    ) if exist_size != file_size else None
                }
            elif os.path.exists(temp_file):
                # start with temp
                start = os.stat(temp_file).st_size
            else:
                # new file
                start = 0

        tasks = []
        size = min(max_concurrency * chunk_size, file_size - start)
        end_chunk = size + start
        queue = asyncio.Queue(maxsize=1024*1024)
        for pos in range(start, end_chunk, chunk_size):
            end = min(pos + chunk_size, file_size) - 1
            queue.put_nowait((pos, end))
        for _ in range(kwargs.get('bandwidth')):
            task = asyncio.create_task(
                self.get_blob(url=url, pos=queue, file=temp_file,
                              chunk_size=chunk_size, md5_check=md5_check)
            )
            tasks.append(task)
        # start queue in tasks
        await queue.join()
        for task in tasks:
            task.cancel()
        # start cancel tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        exception = None
        for i, x in enumerate(sorted(self.buffer[temp_file] , key=lambda x: x['index'])):
            if isinstance(x, Exception):
                exception = x
                os.truncate(temp_file, start + (i * chunk_size))
                file = temp_file
                break
            elif isinstance(x['exception'], (Exception, ClientResponseError)):
                exception = x['exception']
                os.truncate(temp_file, start + (i * chunk_size))
                file = temp_file
                break
            else:
                typed_results.append(x['length'])
        if typed_results:
            position = self._sum_send(typed_results) + start
            typed_results.clear()
        else:
            position = 0

        os.rename(temp_file, file)
        created_time = datetime.datetime.utcnow()
        return {
            "position": position,
            "dst": file,
            "created_time": datetime.datetime.strftime(created_time, "%Y-%m-%dT%H:%M:%S.%f"),
            "region": workspace['location'],
            "access_methods_type": workspace['resources'][0]['type'],
            "exception": exception
        }

    async def get_blob(self, url: URL, file: str, pos: asyncio.queues, **kwargs) -> None:
        while True:
            retry = 3
            start, end = await pos.get()

            while retry:
                try:
                    headers = {
                        "x-ms-version": "2020-04-08",
                        "x-ms-date": datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT'),
                        "x-ms-range": f"bytes={start}-{end}"}
                    if end - start <= 4 * 1024 * 1024:
                        headers["x-ms-range-get-content-md5"] = str(kwargs.get('md5_check'))
                    o_fd = os.open(file, os.O_WRONLY | os.O_CREAT)
                    os.lseek(o_fd, start, os.SEEK_CUR)
                    response = await self.request(
                        url=url,
                        method="GET",
                        headers=headers,
                        fileobj=o_fd, **kwargs)
                    os.close(o_fd)
                    content_md5 = response.attrs.get('x-content-md5')
                    response_content_md5 = response.headers.get('Content-MD5')
                    if response_content_md5:
                        if content_md5 != response_content_md5:
                            raise ValueError(" Chunk data checksum failed")
                    pos.task_done()
                    if self.buffer.get(file):
                        self.buffer[file].append(
                            {"length": end - start + 1,
                             "exception": None,
                             "index": start}
                        )
                    else:
                        self.buffer[file] = [
                            {"length": end - start + 1,
                             "exception": None,
                             "index": start}
                        ]
                    retry = 0
                except ClientResponseError as err:
                    retry -= 1
                    if retry == 0:
                        pos.task_done()
                        if self.buffer.get(file):
                            self.buffer[file].append(
                                {"length": 0,
                                 "exception": err,
                                 "index": start}
                            )
                        else:
                            self.buffer[file] = [
                                {"length": 0,
                                 "exception": err,
                                 "index": start}
                            ]
                    url = self.refresh_service_url(url)
                    pass
                except Exception as err:
                    retry -= 1
                    if retry == 0:
                        pos.task_done()
                        if self.buffer.get(file):
                            self.buffer[file].append(
                                {"length": 0,
                                 "exception": err,
                                 "index": start}
                            )
                        else:
                            self.buffer[file] = [
                                {"length": 0,
                                 "exception": err,
                                 "index": start}
                            ]
                    pass


class FileSystemStorage(BlobStorage):
    """
    Azure Data Lake Storage Gen2 REST APIs to interact with Azure Blob storage
    through a file system interface.
    This interface allows you to create and manage file systems,
    as well as to create and manage directories and files.
    """

    BLOB_SERVICE_URL = "https://{account}.dfs.core.windows.net"

    def __init__(self, workspace):
        super().__init__(workspace)

    async def mkdirs(
            self, uri: URL, permission=0o766, *args, **kwargs
    ) -> bool:
        """
        Create a directory and the destination is overwritten.
        """
        url = self.blob_service_url(uri).update_query("resource=directory")
        headers = {"Content-Type": "application/octet-stream",
                   "Content-Length": "0"}
        if permission is not None:
            headers.setdefault("x-ms-permissions",
                               "0{perm}".format(perm=oct(permission)[2:]))

        try:
            await self.request(url, "PUT", headers=headers,
                               *args, **kwargs)
            return True
        except ClientResponseError as err:
            self.log(logging.ERROR, err)
            return False

    async def rmdir(
            self, uri: URL, *args, **kwargs
    ) -> bool:
        """
        Delete a directory recursively.
        """
        url = self.blob_service_url(uri).update_query("recursive=true")
        try:
            response = await self.request(url, "DELETE", *args, **kwargs)
            while response.headers.get("x-ms-continuation"):
                url = url.update_query("continuation={}".format(
                    response.headers["x-ms-continuation"]
                ))
                response = await self.request(url, "DELETE", *args, **kwargs)
            return True
        except ClientResponseError as err:
            self.log(logging.ERROR, err)
            return False

    async def content(
            self, uri: URL, recursive: bool = False, *args, **kwargs
    ) -> Optional[OrderedDict]:
        c = OrderedDict({"directoryCount": 0,
                         "fileCount": 0,
                         "size": 0,
                         "quota": 0,
                         "spaceConsumed": 0,
                         "spaceQuota": 0,
                         "paths": []})

        def __update(o):
            # Azure API document flaw:
            #   isDirectory property exists only for directory in the current azure API
            #   p['contentLength'] is string, not int
            c["paths"] += o.get("paths", [])
            for p in o.get("paths", []):
                if p.get("isDirectory"):
                    c["directoryCount"] += 1
                else:
                    c["fileCount"] += 1
                    c["size"] += int(p["contentLength"])

        url = self.blob_service_url(uri.with_path(""))
        urx = url.update_query("directory={p}&recursive={r}&resource=filesystem".format(
            p=uri.path.rstrip("/"), r="true" if recursive else "false"
        ))

        try:
            response = await self.request(urx, accept="application/json",
                                          *args, **kwargs)
            __update(response.body)
        except ClientResponseError as err:
            self.log(logging.ERROR, err)
            return None

        while response.headers.get("x-ms-continuation"):
            ury = url.update_query("recursive=false&continuation={continuation}".format(
                continuation=response.headers["x-ms-continuation"]
            ))
            try:
                response = await self.request(ury, accept="application/json",
                                              *args, **kwargs)
                __update(response.body)
            except ClientResponseError as err:
                self.log(logging.ERROR, err)
                return None

        c["spaceConsumed"] = c["size"]
        return c

    async def status(
            self, uri: URL, *args, **kwargs
    ) -> Optional[OrderedDict]:
        url = self.blob_service_url(uri).update_query("action=getStatus")
        try:
            response = await self.request(url, "HEAD",
                                          accept="application/json",
                                          *args, **kwargs)

            result = OrderedDict({"accessTime": response.headers["Date"],
                                  "blockSize": 0,
                                  "group": response.headers["x-ms-group"],
                                  "owner": response.headers["x-ms-owner"],
                                  "permission": response.headers["x-ms-permissions"]})

            if response.headers["x-ms-resource-type"] == "directory":
                result.update({"size": 0,
                               "replication": 0,
                               "type": "DIRECTORY", })
            else:
                result.update({"size": int(response.headers["Content-Length"]),
                               "replication": 1,
                               "type": "FILE", })
            return result
        except ClientResponseError as err:
            self.log(logging.ERROR, err)
            return None

    async def create(
            self, uri: URL, permission=0o766, *args, **kwargs
    ) -> bool:
        """
        Create a new file for uploading data.
        """
        url = URL.build(scheme=uri.scheme,
                        host=uri.host.replace("blob", "dfs"),
                        path=f"/seqslab{uri.path}",
                        query_string="resource=file")

        headers = {"Content-Type": "application/octet-stream",
                   "Content-Length": "0", }
        for _, (k, v) in enumerate(self.auth_headers().items()):
            headers.setdefault(k, v)

        # if permission is not None:
        #     headers.setdefault("x-ms-permissions",
        #                        "0{perm}".format(perm=oct(permission)[2:]))

        try:
            await self.request(url, "PUT",
                               headers=headers,
                               *args, **kwargs)
            return True
        except ClientResponseError as err:
            self.log(logging.ERROR, err)
            return False

    async def append(
            self, uri: URL, file: str, position: int, size: int, md5_check: bool = True,
            *args, **kwargs
    ) -> int:

        url = URL.build(scheme=uri.scheme,
                        host=uri.host.replace("blob", "dfs"),
                        path=f"/seqslab{uri.path}",
                        query_string=f"action=append&position={position}")

        headers = {"Content-Type": "application/octet-stream"}

        for _, (k, v) in enumerate(self.auth_headers().items()):
            headers.setdefault(k, v)

        async with aiofiles.open(file, mode="rb") as f:
            await f.seek(position)
            data = await f.read(size)
            length = len(data)
            headers["Content-Length"] = str(length)
            if md5_check:
                headers["Content-MD5"] = b64encode(md5(data).digest()).decode()
            retry = 5
            while retry:
                retry -= 1
                try:
                    await self.request(url, "PATCH",
                                       headers=headers, data=data,
                                       *args, **kwargs)
                    return length
                except ClientResponseError as err:
                    if retry == 0:
                        self.log(logging.ERROR, err)
                        return 0
                    pass
                except Exception as err:
                    if retry == 0:
                        self.log(logging.ERROR, err)
                        return 0
                    pass

    async def flush(
            self, uri: URL, position: int, *args, **kwargs
    ) -> NoReturn:
        url = URL.build(scheme=uri.scheme,
                        host=uri.host.replace("blob", "dfs"),
                        path=f"/seqslab{uri.path}",
                        query_string=f"action=flush&position={position}")
        headers = {"Content-Type": "application/octet-stream",
                   "Content-Length": "0",
                   "x-ms-content-type": "application/xml"}

        for _, (k, v) in enumerate(self.auth_headers().items()):
            headers.setdefault(k, v)
        await self.request(url, "PATCH",
                           headers=headers,
                           *args, **kwargs)

    async def upload(
            self, uri: URL, file: str,
            chunk_size: int = 64 * 1024 * 1024,
            max_concurrency: int = 0,
            md5_check: bool = False,
            *args, **kwargs
    ) -> dict:
        """
        Asynchronous single file uploading
        :return the number of bytes sent.
        """
        assert os.path.isfile(file)

        rel = kwargs.get("relative_path", None)
        if rel:
            path = os.path.join(uri.path, rel)
            uri = uri.with_path(path)
        else:
            if uri.path.endswith("/"):
                name = os.path.basename(file)
                uri = uri.with_name(name)

        uri = self.blob_service_url(uri=uri, **kwargs)
        created = await self.create(uri, **kwargs)
        if not created:
            return {"position": 0, "dst": uri.with_query("")}

        try:
            concurrency = int(max_concurrency) or 8 * len(os.sched_getaffinity(0))
        except AttributeError:
            concurrency = 8 * os.cpu_count()

        position = 0
        file_size = os.stat(file).st_size
        while position < file_size:
            size = min(concurrency * chunk_size, file_size - position)
            end_chunk = size + position
            tasks = [self.append(uri, file, pos, chunk_size, md5_check,
                                 **kwargs)
                     for pos in range(position, end_chunk, chunk_size)]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            typed_results = List()
            [typed_results.append(x) for x in results]
            sent = BlobStorage._sum_send(typed_results)
            position += sent
            await self.flush(uri, position, **kwargs)

            if sent != size:
                # it is safe to continue since the position is
                # always set to the last successful append blob.
                # this is extremely rare since tasks would
                # automatically retry.
                continue

        # end while
        return {"position": position, "dst": uri.with_query("")}

    async def download(
            self, uri: URL, file: str,
            chunk_size: int = 4 * 1024 * 1024,
            max_concurrency: int = 0,
            overwrite=True,
            *args, **kwargs
    ) -> int:
        """
        Use HTTP Range request header (ex: bytes=0-70225) to
        download in parallel and asynchronously.
        Enable MD5 check when chunk_size <= 4MB
        :return the file size downloaded
        """
        assert not overwrite and not os.path.exists(file)

        if os.path.isfile(file):
            os.remove(file)

        status = await self.status(uri, *args, **kwargs)
        if status is None or not status.get("size"):
            raise LookupError("fail to lookup file status or size is 0")

        headers = {}
        if chunk_size <= 4 * 1014 * 1024:
            headers.setdefault("x-ms-range-get-content-md5", "true")

        try:
            concurrency = max_concurrency or 8 * len(os.sched_getaffinity(0))
        except AttributeError:
            concurrency = 8 * os.cpu_count()

        url = self.blob_service_url(uri)
        position = 0
        file_size = status.get("size")
        while position < file_size:
            # prepare asynchronous tasks given concurrency and Range request
            data_size = min(concurrency * chunk_size, file_size - position)
            tasks = [super().download(
                url, file + ".{}".format(start), chunk_size,
                md5_check=bool(headers.get("x-ms-range-get-content-md5")),
                headers=dict([(k, v) for k, v in headers.items()] +
                             [("Range", "bytes={start}-{end}".format(
                                 start=start, end=start + chunk_size - 1))]),
                *args, **kwargs)
                for start in range(position, data_size, chunk_size)]

            # execute download tasks concurrently and get task Response
            results = await asyncio.gather(*tasks, return_exceptions=True)

            o_fd = os.open(file, os.O_WRONLY | os.O_CREAT)
            os.lseek(o_fd, 0, os.SEEK_END)
            preposition = position
            for idx, response in enumerate(results):
                try:
                    start = int(re.split(" |-", response.headers.get("Content-Range"))[1])
                    length = int(response.headers.get("Content-Length"))

                    if (response.attrs.get("x-content-md5") ==
                            response.headers.get("Content-MD5") and
                            position == start):
                        # append file and advance position
                        i_fd = os.open(file + f".{start}", os.O_RDONLY)
                        sent = 1
                        offset = 0
                        while sent and sent != length:
                            sent = await sendfile(o_fd, i_fd, offset, length)
                            offset += sent
                        os.close(i_fd)
                        position += length

                    os.remove(file + f".{start}")
                except AttributeError:
                    # response is an Exception
                    os.remove(file + f".{preposition + idx * chunk_size}")
            # end for
            os.close(o_fd)

        # end while
        return position
