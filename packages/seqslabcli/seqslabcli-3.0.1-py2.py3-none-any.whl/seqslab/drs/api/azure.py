from .base import DRSregister
import os
from datetime import datetime
from tenacity import retry, wait_fixed, stop_after_attempt
import requests
from yarl import URL
from seqslab.auth.commands import BaseAuth
from functools import lru_cache
from termcolor import cprint
import hashlib
from .biomimetype import get_mime_type
from typing import List
WAIT_TWO_SECOND = wait_fixed(2)


class AzureDRSregister(DRSregister):

    def __init__(self, workspace):
        """
        :param workspace: resource group in Azure
        """
        self._workspace = workspace

    def _get_dir_size(self, dir_path):
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(dir_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        return total_size

    @lru_cache(maxsize=16)
    @retry(stop=stop_after_attempt(3), wait=WAIT_TWO_SECOND, reraise=True)
    def workspace(self, name: str) -> dict:
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please signin first!")
        url = DRSregister.DRS_RESOURCES_URL.format(name=name)
        with requests.get(url, headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=WAIT_TWO_SECOND, reraise=True)
    def blob_property(self, token: str, blob_url: str, is_file: bool) -> dict:
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        headers = {"Authorization": f"Bearer {token}",
                   "x-ms-date": date,
                   "x-ms-version": "2020-10-02"}
        if is_file:
            headers["x-ms-range"] = "bytes=0-0"
        with requests.get(blob_url, headers=headers) as response:
            if response.status_code not in range(200, 210):
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.headers

    def bundle_register(self, src: str, upload_result: list, access_tier: str,
                        description: str, aliases: list, metadata: dict, tags: list) -> str:
        child_file_list = {}
        child_dir_list = {}
        workspace = self.workspace(name=self._workspace)
        storage_token = workspace["tokens"]["Microsoft.Storage/storageAccounts"]
        region = workspace["resources"][0]["location"]
        access_methods_type = workspace["resources"][0]["type"]
        access_tier = access_tier

        for root, folder_list, file_list in os.walk(src, topdown=False):
            child_file_list[root] = []
            child_dir_list[root] = []
            mime_type = []
            size = []
            created_time_transformed = []
            checksum = []
            access_url = []
            if folder_list:
                for folder in folder_list:
                    if child_dir_list[os.path.join(root, folder)]:
                        child_file_list[os.path.join(root, folder)].extend(child_dir_list[os.path.join(root, folder)])
                        del child_dir_list[os.path.join(root, folder)]
                    if child_file_list[os.path.join(root, folder)]:
                        kwargs = {
                            "name": [folder],
                            "file_type": ["bundle"],
                            "mime_type": [""],
                            "contents": [[{"drs_id": id} for id in child_file_list[os.path.join(root, folder)]]]
                        }
                        try:
                            bundle_id = self.create_drsobjects(
                                drs_type="bundle",
                                metadata=[{}],
                                description=[""],
                                aliases=[[]],
                                tags=[[]], **kwargs
                            )
                            for drs_id in bundle_id:
                                cprint(f"DRS sub_bundle object: {drs_id} create complete", "yellow")
                        except Exception as error:
                            raise error
                        del child_file_list[os.path.join(root, folder)]
                        child_dir_list[root].extend(bundle_id)

            if file_list:
                abs_src = list(
                    map(lambda filename, root: os.path.join(root, filename), file_list, [root] * len(file_list)))
                file_types = [os.path.splitext(os.path.basename(src))[1].lstrip('.') for src in abs_src]
                child_file = list(
                    map(lambda info: info if info.src in abs_src else None, upload_result)
                )
                child_file = [child for child in child_file if child]
                for child in child_file:
                    filename, file_extension = os.path.splitext(os.path.basename(child.src))
                    mime_type.append(get_mime_type().mime_type(file_extension))
                    blob_property = self.blob_property(token=storage_token,
                                                       blob_url=child.dst,
                                                       is_file=True)
                    created_time = datetime.strptime(blob_property['x-ms-creation-time'],
                                                     '%a, %d %b %Y %H:%M:%S GMT')
                    created_time_transformed.append(
                        datetime.strftime(created_time, "%Y-%m-%dT%H:%M:%S.%f"))

                    size.append(os.stat(child.src).st_size)
                    checksum.append(child.checksum)
                    access_url.append({
                        "url": AzureDRSregister.get_abfss_path(URL(child.dst)),
                        "headers": {}
                    })
                kwargs = {
                    "created_time": created_time_transformed,
                    "updated_time": created_time_transformed,
                    "size": size,
                    "access_methods_type": [access_methods_type] * len(file_list),
                    "access_url": access_url,
                    "access_tier": [access_tier] * len(file_list),
                    "region": [region] * len(file_list),
                    "checksum": checksum,
                    "checksum_type": ["sha256"] * len(file_list)
                }
                try:
                    child_file_id = self.create_drsobjects(drs_type="blob", name=file_list,
                                                       mime_type=mime_type,
                                                       file_type=file_types,
                                                       description=[""] * len(file_list),
                                                       aliases=[[]] * len(file_list),
                                                       metadata=[{}] * len(file_list),
                                                       tags=[[]] * len(file_list), **kwargs)
                    for drs_id in child_file_id:
                        cprint(f"DRS blob object: {drs_id} create complete", "yellow")
                except Exception as error:
                    raise error
                child_file_list[root].extend(child_file_id)
            if os.path.abspath(root) == os.path.abspath(src):
                if child_dir_list[root]:
                    child_file_list[root].extend(child_dir_list[root])
                    del child_dir_list[root]
                try:
                    kwargs = {
                        "name": [os.path.basename(root)],
                        "file_type": ["bundle"],
                        "mime_type": [""],
                        "contents": [[{"drs_id": id} for id in child_file_list[root]]]
                    }
                    bundle_id = self.create_drsobjects(
                        drs_type="bundle",
                        metadata=[metadata],
                        description=[description],
                        aliases=[aliases],
                        tags=[tags], **kwargs
                    )
                except Exception as error:
                    raise error
                child_dir_list.clear()
                child_file_list.clear()
                return bundle_id[0]

    def blob_register(self, src: str, upload_result: list, access_tier: str,
                      description: str, aliases: list, metadata: dict, tags: list) -> str:
        workspace = self.workspace(name=self._workspace)
        storage_token = workspace["tokens"]["Microsoft.Storage/storageAccounts"]
        region = workspace["resources"][0]["location"]
        access_methods_type = workspace["resources"][0]["type"]
        access_tier = access_tier

        checksum, mime_type, file_type, created_time = self.get_blob_property(storage_token,
                                                                              src,
                                                                              upload_result[0].dst,
                                                                              [result.checksum for result in
                                                                               upload_result])
        size = os.stat(src).st_size
        if os.path.isdir(src):
            size = self._get_dir_size(src)
            src = src.rstrip('/')

        # for directory as blob scenario, access_url should point to gen2 path as a whole
        dst = upload_result[0].dst if os.path.isfile(str(src)) else os.path.commonprefix(
            [res.dst for res in upload_result])

        kwargs = {
            "name": [os.path.basename(src)],
            "mime_type": [mime_type],
            "file_type": [file_type],
            "created_time": [datetime.strftime(created_time, "%Y-%m-%dT%H:%M:%S.%f")],
            "updated_time": [datetime.strftime(created_time, "%Y-%m-%dT%H:%M:%S.%f")],
            "size": [size],
            "access_methods_type": [access_methods_type],
            "access_url": [{
                "url": AzureDRSregister.get_abfss_path(URL(dst)),
                "headers": {}
            }],
            "access_tier": [access_tier],
            "region": [region],
            "checksum": [checksum],
            "checksum_type": ["sha256"],
            "description": [description],
            "aliases": [aliases],
            "metadata": [metadata],
            "tags": [tags]
        }
        blob_id = self.create_drsobjects(drs_type="blob", **kwargs)

        return blob_id[0]

    def get_blob_property(self, storage_token, src, dst, dst_checksums):

        if os.path.isfile(src):
            blob_property = self.blob_property(token=storage_token, blob_url=dst, is_file=True)
            checksum = dst_checksums[0]
            _, file_extension = os.path.splitext(os.path.basename(src))
            file_type = file_extension
            mime_type = get_mime_type().mime_type(file_extension)
        else:
            blob_property = self.blob_property(token=storage_token, blob_url=dst, is_file=False)
            file_checksums = dst_checksums
            file_checksums.sort()
            encode_text = ''.join(map(str, file_checksums)).encode()
            checksum = hashlib.sha256(encode_text).hexdigest()
            mime_type = "unknown"
            file_type = "folder"
        created_time = datetime.strptime(blob_property['x-ms-creation-time'],
                                         '%a, %d %b %Y %H:%M:%S GMT')
        return checksum, mime_type, file_type, created_time

    def register(self, drs_type: str, description: str, aliases: list, metadata: dict, tags: list, **kwargs) -> str:
        src = kwargs.get("src")
        upload = kwargs.get("upload")
        access_tier = kwargs.get("access_tier")
        try:
            if drs_type == "bundle":
                object_id = self.bundle_register(src=str(src), upload_result=upload,
                                                 access_tier=access_tier, description=description,
                                                 aliases=aliases, metadata=metadata, tags=tags)
            else:
                object_id = self.blob_register(src=str(src), upload_result=upload,
                                               access_tier=access_tier, description=description,
                                               aliases=aliases, metadata=metadata, tags=tags)
            return object_id
        except Exception as error:
            raise error

    @staticmethod
    def get_blob_info(_url: URL):
        # https://storageaccount.blob.core.windows.net/seqslab/drs/drs_id/
        _storage = _url.host.split('.')[0]
        container_blob_name = _url.path.strip('/').split('/')
        _container = container_blob_name[0]
        _blob = '/'.join(container_blob_name[1::])
        _sdd = -1
        if _url.path[-1] == '/':
            _sdd = _url.path.count('/') - 2  # remove the container and last
        return _storage, _container, _blob, _sdd

    @staticmethod
    def get_abfss_path(url: URL):
        storage, container, blob, _ = AzureDRSregister.get_blob_info(url)
        return f'abfss://{container}@{storage}.dfs.core.windows.net/{blob}'

    def dst_checking(self, dst: str) -> None:
        root_path = self.root_path(workspace_name=self._workspace)
        if len(root_path.strip('/')) >= len(dst.strip('/')):
            raise ValueError(f'Make sure the common path of all the dsts is longer than the root.')

    def get_access_url(self, dsts_list: list, access_methods: list, access_method_infos: list, index: int) \
            -> List[List[URL]]:
        if len(dsts_list) == 2:
            for access_method in access_methods:
                if access_method.get('access_url'):
                    if access_method.get('type') in ['https', 'http']:
                        url = URL(access_method.get('access_url').get('url'))
                        if url and 'blob.core.windows.net' in url.host:
                            dsts_list[0].append(url)

                    elif access_method.get('type') in ['abfss', 'abfs']:
                        url = URL(access_method.get('access_url').get('url'))
                        if url:
                            dsts_list[1].append(url)
                else:
                    raise ValueError(f'Index {index}, has no access_url in access_methods.')
        elif len(dsts_list) == 0:
            for access_method in access_methods:
                if access_method.get('access_url'):
                    if access_method.get('type') in ['https', 'http']:
                        url = URL(access_method.get('access_url').get('url'))
                        if 'blob.core.windows.net' in url.host:
                            dsts_list.append([url])
                            access_method['access_url'].pop('url')
                            access_method_infos.append(access_method)
                    elif access_method.get('type') in ['abfss', 'abfs']:
                        url = URL(access_method.get('access_url').get('url'))
                        if url:
                            dsts_list.append([url])
                            access_method['access_url'].pop('url')
                            access_method_infos.append(access_method)
                else:
                    raise ValueError(f'Index {index}, has no access_url in access_methods.')
        else:
            raise ValueError(f'Enter a valid stdin template, lost one access_url in access_methods.')
        return dsts_list
