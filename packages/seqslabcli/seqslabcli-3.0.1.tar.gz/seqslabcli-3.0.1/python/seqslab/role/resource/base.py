import requests
import logging
from tenacity import retry, wait_fixed, stop_after_attempt
from seqslab.auth.commands import BaseAuth
from seqslab.exceptions import exception_handler
from seqslab import role
import json


class BaseResource:
    logger = logging.getLogger()

    MGMT_ROLE_URL = f"https://{role.API_HOSTNAME}/management/{role.__version__}/roles/"

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def request_wrapper(
            callback,
            url,
            headers,
            status,
            data=None,
            stream=False,
    ) -> requests.Response:
        with callback(url, headers=headers, data=data, stream=stream) as r:
            if r.status_code in status:
                return r
            else:
                raise requests.HTTPError(json.loads(r.content))

    @exception_handler
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2), reraise=True)
    def list_role(self, **kwargs) -> dict:
        token = BaseAuth.get_token().get("tokens").get("access")
        r = self.request_wrapper(
            callback=requests.get,
            url=BaseResource.MGMT_ROLE_URL,
            headers={"Authorization": f"Bearer {token}"},
            status=[200])
        return r.json()
