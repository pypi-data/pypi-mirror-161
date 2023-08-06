import requests
import logging
from tenacity import retry, wait_fixed, stop_after_attempt
from seqslab.auth.commands import BaseAuth
from seqslab import trs, drs, wes, workspace
import json
from typing import List, Dict
from functools import lru_cache

class BaseResource:
    logger = logging.getLogger()

    TRS_BASE_URL = f"https://{trs.API_HOSTNAME}/trs/{trs.__version__}"
    TRS_WORKSPACE_URL = f"{TRS_BASE_URL}/service-info/workspaces/"

    DRS_BASE_URL = f"https://{drs.API_HOSTNAME}/ga4gh/drs/{drs.__version__}"
    DRS_WORKSPACE_URL = f"{DRS_BASE_URL}/service-info/workspaces/"

    WES_BASE_URL = f"https://{wes.API_HOSTNAME}/wes/{wes.__version__}"
    WES_WORKSPACE_URL = f"{WES_BASE_URL}/service-info/workspaces/"
    WES_CONTAINER_REGISTRY_URL = f"{WES_WORKSPACE_URL}{{name}}/container-registries/"

    MGMT_BASE_URL = f"https://{workspace.API_HOSTNAME}/management/{workspace.__version__}"
    MGMT_WORKSPACE_URL = f"{MGMT_BASE_URL}/workspaces/"
    MGMT_STATUS_URL = f"{MGMT_WORKSPACE_URL}status/{{task_id}}/"

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    @lru_cache(maxsize=16)
    def list_workspaces(**kwargs) -> List[dict]:
        token = BaseAuth.get_token().get("tokens").get("access")
        with requests.get(url=kwargs.get("system"),
                          headers={"Authorization": f"Bearer {token}"},
                          params={"expand": kwargs.get('expand'),
                                  "force": kwargs.get('force')}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(f"{json.loads(response.content)}")
            return response.json()

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=False)
    def create_workspaces(name, location, **kwargs) -> dict:
        token = BaseAuth.get_token().get("tokens").get("access")
        with requests.put(url=BaseResource.MGMT_WORKSPACE_URL,
                          headers={"Authorization": f"Bearer {token}"},
                          data={
                              "workspace": name,
                              "location": location
                          }) as response:
            if response.status_code not in [202]:
                raise requests.HTTPError(json.loads(response.content))
            return response.json()

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def status(task_id, **kwargs) -> dict:
        token = BaseAuth.get_token().get("tokens").get("access")
        with requests.get(url=BaseResource.MGMT_STATUS_URL.format(task_id=task_id),
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(json.loads(response.content))
            return response.json()

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    @lru_cache(maxsize=16)
    def container_registry(workspace, **kwargs) -> dict:
        token = BaseAuth.get_token().get("tokens").get("access")
        url = BaseResource.WES_CONTAINER_REGISTRY_URL.format(name=workspace)
        with requests.get(url=url,
                          headers={"Authorization": f"Bearer {token}"}) as response:
            if response.status_code not in [requests.codes.ok]:
                raise requests.HTTPError(json.loads(response.content))
            return json.loads(response.content)
