import json

import requests
import logging
from seqslab.auth.commands import BaseAuth
from seqslab.trs import __version__, API_HOSTNAME
from abc import ABC
from tenacity import retry, wait_fixed, stop_after_attempt
from .template import get_template
import os


class TRSregister(ABC):
    logger = logging.getLogger()

    TRS_TOOL_URL = f"https://{API_HOSTNAME}/trs/{__version__}/tools/"
    TRS_TOOLVERSION_URL = f"{TRS_TOOL_URL}{{tool_id}}/versions/"
    TRS_TOOLFILE_URL = f"{TRS_TOOLVERSION_URL}{{version_id}}/{{descriptor_type}}/files/"
    TRS_TOOL_EXEC_FILE_URL = f"{TRS_TOOLVERSION_URL}{{version_id}}/{{descriptor_type}}/execution_file/"

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def post_tool(data: dict) -> dict:
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please signin first!")

        with requests.post(url=TRSregister.TRS_TOOL_URL,
                           headers={"Authorization": f"Bearer {token}"},
                           json=data) as response:
            if response.status_code not in [requests.codes.created]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.json()

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def post_version(data: dict, tool_id: str, workspace: str) -> dict:
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please signin first!")

        with requests.post(url=TRSregister.TRS_TOOLVERSION_URL.format(tool_id=tool_id),
                           headers={"Authorization": f"Bearer {token}"},
                           json=data,
                           params={"workspace": workspace}) as response:
            if response.status_code not in [requests.codes.created]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.json()

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def post_file(data: dict, zip_file: str, tool_id: str, version_id: str,
                  descriptor_type: str) -> str:
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please signin first!")

        files = {
            "file": (f"{os.path.basename(zip_file)}", open(zip_file, 'rb'), 'application/zip'),
            "file_info": ("", json.dumps(data))

        }
        workflow_url = TRSregister.TRS_TOOLFILE_URL.format(tool_id=tool_id,
                                                           version_id=version_id,
                                                           descriptor_type=descriptor_type)
        with requests.post(url=workflow_url,
                           headers={"Authorization": f"Bearer {token}"},
                           files=files) as response:
            if response.status_code not in [requests.codes.created]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return workflow_url

    def tool(self, tool_name: str, **kwargs):
        data = get_template("tool").create(
            toolclass_name=kwargs.get('toolclass_name'),
            toolclass_description=kwargs.get('toolclass_description'),
            tool_name=tool_name,
            description=kwargs.get("description"),
            aliases=kwargs.get("aliases", []),
            checker_url=kwargs.get("checker_url"),
            has_checker=kwargs.get('has_checker'),
            id=kwargs.get('id')
        )
        return self.post_tool(
            data=data
        )

    def version(self, tool_id: str, version_name: str, version_id: str,
                descriptor_type: str, images: list, **kwargs):
        data = get_template("toolversion").create(
            version_name=version_name,
            version_id=version_id,
            descriptor_type=descriptor_type,
            images=images,
            **kwargs
        )
        return self.post_version(
            data=data,
            tool_id=tool_id, workspace=kwargs.get("workspace", None)
        )

    def file(self, tool_id: str, version_id: str, descriptor_type: str,
             toolfile_json: dict, zip_file: str):
        return self.post_file(
            data=get_template("toolfile").create(
                toolfile_json=toolfile_json
            ),
            zip_file=zip_file,
            tool_id=tool_id,
            version_id=version_id,
            descriptor_type=descriptor_type
        )

    @staticmethod
    def register():
        try:
            return 0
        except Exception as error:
            raise error

    @staticmethod
    def get_tool():
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please signin first!")

        with requests.get(url=TRSregister.TRS_TOOL_URL,
                          headers={"Authorization": f"Bearer {token}"},
                          stream=True
                          ) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.json()

    @staticmethod
    def get_execs_json(workflow_url: str, download_path: str):
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please signin first!")

        url = workflow_url.replace('files', 'execs')
        with requests.get(url=url,
                          headers={"Authorization": f"Bearer {token}"},
                          stream=True
                          ) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")

            with open(download_path, 'w') as fd:
                fd.write(response.json().get('content'))

            return response.status_code

    @staticmethod
    def delete_version(tid: str, vid: str):
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please signin first!")
        with requests.delete(url=f"{TRSregister.TRS_TOOLVERSION_URL.format(tool_id=tid)}/{vid}",
                             headers={"Authorization": f"Bearer {token}"},
                             stream=True
                             ) as response:
            if response.status_code not in [requests.codes.no_content]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")
            return response.content

    @staticmethod
    def get_file(tool_id: str, version_id: str, download_path: str, descriptor_type: str):
        try:
            token = BaseAuth.get_token().get("tokens").get("access")
        except KeyError:
            raise KeyError(f"No tokens, Please sigin first!")

        url = f'{TRSregister.TRS_TOOLFILE_URL}?expand=true&format=zip'
        with requests.get(url=url.format(tool_id=tool_id, version_id=version_id, descriptor_type=descriptor_type, ),
                          headers={"Authorization": f"Bearer {token}"},
                          stream=True
                          ) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{response.status_code}: {repr(response.text)}")

            with open(download_path, 'wb') as fd:
                for chunk in response.iter_content(chunk_size=128):
                    fd.write(chunk)

            return response.status_code
