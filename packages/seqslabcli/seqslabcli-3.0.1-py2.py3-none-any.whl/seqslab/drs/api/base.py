import requests
import logging
from seqslab.auth.commands import BaseAuth
from seqslab.drs import __version__, API_HOSTNAME
from tenacity import retry, wait_fixed, stop_after_attempt
from .template import get_template
from typing import List, NamedTuple
import json
import hashlib
import os
from yarl import URL
from functools import lru_cache

WAIT_TWO_SECOND = wait_fixed(2)


class CopyResult(NamedTuple):
    id: str
    name: int
    mime_type: str
    file_type: str
    description: str
    self_uri: str
    size: int
    version: str
    created_time: str
    updated_time: str
    metadata: dict
    aliases: list
    tags: list
    checksums: dict
    access_methods: dict

    def __str__(self):
        return json.dumps(
            {
                'id': self.id,
                'name': self.name,
                'mime_type': self.mime_type,
                'file_type': self.file_type,
                'description': self.description,
                'self_uri': self.self_uri,
                'size': self.size,
                'version': self.version,
                'created_time': self.created_time,
                'updated_time': self.updated_time,
                'metadata': self.metadata,
                'aliases': self.aliases,
                'tags': self.tags,
                'checksums': self.checksums,
                'access_methods': self.access_methods
            }
        )


class DRSregister:
    logger = logging.getLogger()

    DRS_OBJECT_URL = f"https://{API_HOSTNAME}/ga4gh/drs/{__version__}/objects/"
    DRS_OBJECT_URL_ID = f"https://{API_HOSTNAME}/ga4gh/drs/{__version__}/objects/{{object_id}}/"
    DRS_WORKSPACE_URL = f"https://{API_HOSTNAME}/ga4gh/drs/{__version__}/service-info/workspaces/"
    DRS_RESOURCES_URL = f"{DRS_WORKSPACE_URL}{{name}}/resources/"
    DRS_UPLOAD_URL = f"https://{API_HOSTNAME}/ga4gh/drs/{__version__}/objects/upload/"

    @lru_cache(maxsize=16)
    def root_path(self, workspace_name: str) -> str:
        token = BaseAuth.get_token().get("tokens").get("access")
        with requests.get(self.DRS_UPLOAD_URL,
                          headers={"Authorization": f"Bearer {token}"},
                          params={"name": workspace_name,
                                  "path": '/'}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.text}")
            return URL(response.json().get('url')).path

    @retry(stop=stop_after_attempt(3), wait=WAIT_TWO_SECOND, reraise=True)
    def post_drs(self, data):
        """
        api drs object
        :param: data
        :response: drs object json
        """
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please sign in first!")
        bundle = False
        if isinstance(data, list):
            if data[0]['file_type'] == "bundle":
                bundle = True
        else:
            if data['file_type'] == "bundle":
                bundle = True
        with requests.post(url=DRSregister.DRS_OBJECT_URL,
                           headers={"Authorization": f"Bearer {token}"},
                           json=data,
                           params={"bundle": bundle}) as response:
            if response.status_code not in [requests.codes.created]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.json()

    @retry(stop=stop_after_attempt(3), wait=WAIT_TWO_SECOND, reraise=True)
    def patch_drs(self, data, drs_id) -> dict:
        """
        partial update drs object
        :param: data
        :response: drs object json
        """
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please sign in first!")
        url = DRSregister.DRS_OBJECT_URL_ID.format(object_id=drs_id)
        with requests.patch(url=url,
                            headers={"Authorization": f"Bearer {token}"},
                            json=data) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.json()

    @staticmethod
    def patch_template(name: str = None, tags: List[str] = [], metadata: dict = {}, checksum: str = None,
                       checksum_type: str = None,
                       updated_time: str = None, **kwargs) -> dict:
        """
        return only one template
        :param: drs_type, description, aliases, metadata, tags
        :**kwargs(blob): name, mime_type, file_type, created_time, updated_time, size, access_methods_type,
                        access_url, access_tier, region, checksum, checksum_type
        :**kwargs(bundle):
        """
        checksums = None
        if checksum and checksum_type:
            checksums = [{
                "checksum": checksum,
                "checksum_type": checksum_type
            }]
        template = get_template().patch(name=name,
                                        tags=tags,
                                        metadata=metadata,
                                        checksums=checksums,
                                        updated_time=updated_time)
        return template

    @retry(stop=stop_after_attempt(3), wait=WAIT_TWO_SECOND, reraise=True)
    def get_drs(self, drs_id):
        """
        api drs object
        :response: drs object json
        """
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please sign in first!")
        with requests.get(url=self.DRS_OBJECT_URL_ID.format(object_id=drs_id),
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.json()

    def create_drsobjects(self, drs_type: str, payloads: List[dict]):
        request_body = [get_template(drs_type).create(**payload) for payload in payloads]
        drs_objects = self.post_drs(request_body)
        results = [CopyResult(
            id=obj.get('id'),
            name=obj.get('name'),
            mime_type=obj.get('mime_type'),
            file_type=obj.get('file_type'),
            description=obj.get('description'),
            self_uri=obj.get('self_uri'),
            size=obj.get('size'),
            version=obj.get('version'),
            created_time=obj.get('created_time'),
            updated_time=obj.get('updated_time'),
            metadata=obj.get('metadata'),
            aliases=obj.get('aliases'),
            tags=obj.get('tags'),
            access_methods=obj.get('access_methods'),
            checksums=obj.get('checksums'),
        )._asdict() for obj in drs_objects]
        return results

    def create_payload(self, stdin: List[dict], type: str, **kwargs) -> List[dict]:
        if type == 'file-blob':
            payload = stdin
        else:
            payload = self.folder_blob(stdin)
        return payload

    def dst_checking(self, dst: str) -> None:
        """ NotImplementet """
        return

    def get_access_url(self, dsts_list: list, access_methods: list, access_method_infos: list, index: int) \
            -> List[List[URL]]:
        """ NotImplementet """
        return dsts_list

    def folder_blob(self, stdin: List[dict]) -> List[dict]:
        checksums = []
        sizes = []
        dsts_list = []
        access_method_infos = []
        created_times = []
        for i, v in enumerate(stdin):
            if v.get('checksums'):
                checksums.append(v.get('checksums')[0].get('checksum'))
            else:
                raise ValueError(f'Index {i}, has no checksums.')
            sizes.append(v.get('size'))
            if v.get('access_methods'):
                 self.get_access_url(
                    dsts_list=dsts_list, access_methods=v.get('access_methods'),
                    access_method_infos=access_method_infos, index=i)
            else:
                raise ValueError(f'Index {i}, has no access_methods.')
            created_times.append(v.get('created_time'))
        folder_stdin = stdin[0].copy()
        folder_stdin['checksums'][0]['checksum'] = DRSregister.concat_checksum(checksums=checksums)
        folder_stdin['size'] = DRSregister.sum_fsize(sizes=sizes)
        folder_stdin['created_time'] = DRSregister.min_time(times=created_times)
        folder_stdin['mime_type'] = "folder"
        folder_stdin['file_type'] = "folder"
        folder_stdin['access_methods'].clear()
        for i, dsts in enumerate(dsts_list):
            folder_stdin['access_methods'].append(access_method_infos[i])
            folder_stdin['access_methods'][i]['access_url']['url'] = self.common_root(dsts=dsts)
        folder_stdin['name'] = os.path.basename(folder_stdin['access_methods'][0]['access_url']['url'].strip('/'))
        return [folder_stdin]

    @staticmethod
    def concat_checksum(checksums: List[str]) -> str:
        if not all(checksums) or not checksums:
            raise ValueError('Make sure all the checksums are filled.')
        checksums.sort()
        encode_text = ''.join(map(str, checksums)).encode()
        checksum = hashlib.sha256(encode_text).hexdigest()
        return checksum

    @staticmethod
    def sum_fsize(sizes: List[int]) -> int:
        if not all(sizes) or not sizes:
            raise ValueError('Make sure all the sizes are filled.')
        return sum(sizes)

    def common_root(self, dsts: List[URL]) -> str:
        if not all(dsts) or not dsts:
            raise ValueError('Make sure all the dsts are filled.')
        schemes = set([dst.scheme for dst in dsts])
        user = set([dst.user for dst in dsts])
        hosts = set([dst.host for dst in dsts])
        if len(schemes) == 1 and len(hosts) == 1 and len(user) == 1:
            path = f'{os.path.commonpath([dst.path for dst in dsts])}/'
            root_dst = str(URL.build(
                user=next(iter(user)),
                scheme=next(iter(schemes)),
                host=next(iter(hosts)),
                path=path
            ))
            self.dst_checking(dst=root_dst)
        else:
            raise ValueError(f'Make sure all the dsts have a common root.')
        return root_dst

    @staticmethod
    def min_time(times: List[str]) -> str:
        if not all(times) or not times:
            raise ValueError('Make sure all the created_times are filled.')
        return min(times)

    def change(self, drs_id: str, **kwargs):
        if kwargs.get('checksums'):
            kwargs['checksum'] = kwargs['checksums'][0].get('checksum')
            kwargs['checksum_type'] = kwargs['checksums'][0].get('type')
        if kwargs.get('created_time') and not kwargs.get('updated_time'):
            kwargs['updated_time'] = kwargs.get('created_time')
        request_body = DRSregister.patch_template(**kwargs)
        obj = self.patch_drs(data=request_body, drs_id=drs_id)
        results = CopyResult(
            id=obj.get('id'),
            name=obj.get('name'),
            mime_type=obj.get('mime_type'),
            file_type=obj.get('file_type'),
            description=obj.get('description'),
            self_uri=obj.get('self_uri'),
            size=obj.get('size'),
            version=obj.get('version'),
            created_time=obj.get('created_time'),
            updated_time=obj.get('updated_time'),
            metadata=obj.get('metadata'),
            aliases=obj.get('aliases'),
            tags=obj.get('tags'),
            access_methods=obj.get('access_methods'),
            checksums=obj.get('checksums')
        )._asdict()
        return results
