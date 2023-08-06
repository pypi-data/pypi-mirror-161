# cli code
import json
# python module
from os.path import abspath, dirname
from unittest.mock import patch

# cli code
import requests
from seqslab.user.commands import BaseUser
from seqslab.user.resource.base import BaseResource

user_data_location = f'{dirname(abspath(__file__))}'
fixtures_dir = f'{user_data_location}/fixtures/'
list_resp = 'list_users.json'
get_resp = 'get_users.json'
add_resp = 'add_users.json'
update_resp = 'update_users.json'


class MockResource(BaseResource):

    def list_user(self, **kwargs) -> dict:
        with open(f'{fixtures_dir}/{list_resp}', 'r') as f:
            ret = json.load(f)
        return ret

    def get_user(self, user_id, **kwargs) -> dict:
        with open(f'{fixtures_dir}/{get_resp}', 'r') as f:
            ret = json.load(f)
        return ret

    def add_user(self, email, roles, active, name, **kwargs) -> dict:
        with open(f'{fixtures_dir}/{add_resp}', 'r') as f:
            ret = json.load(f)
        return ret

    def patch_user(self, user_id, payload, **kwargs) -> dict:
        with open(f'{fixtures_dir}/{update_resp}', 'r') as f:
            ret = json.load(f)
        return ret

    def delete_user(self, user_id, **kwargs) -> requests.Response:
        return requests.Response()


class MockUser(BaseUser):
    """
    Mock user commands
    """
    workspace = 'test'

    def __init__(self):
        pass


user_patch = patch('seqslab.user.commands.User', MockUser)
resource_patch = patch('seqslab.user.resource.azure.AzureResource', MockResource)

from unittest import TestCase
from seqslab.tests.util import TestShell


class BasicTest(TestCase):
    mock_command = MockUser()
    workspace = 'test'
    shell = TestShell


@user_patch
@resource_patch
class CommandSpecTest(BasicTest):

    def test_list(self):
        user = MockUser()
        shell = TestShell(commands=[user.list])
        exit_code = shell.run_cli_line(f"test_shell list")
        self.assertEqual(0, exit_code)

    def test_get(self):
        user = MockUser()
        shell = TestShell(commands=[user.get])
        exit_code = shell.run_cli_line(f"test_shell get --id eonn7fdx5bt6u")
        self.assertEqual(0, exit_code)

    def test_add(self):
        user = MockUser()
        shell = TestShell(commands=[user.add])
        exit_code = shell.run_cli_line(
            f'test_shell add --email td@example.com --name testdrive --active --roles "Data hub writer"')
        self.assertEqual(0, exit_code)

    def test_update(self):
        user = MockUser()
        shell = TestShell(commands=[user.update])
        exit_code = shell.run_cli_line(
            'test_shell update --email td@example.com --id usr_kKVqPIIdH3Ezbl1')
        self.assertEqual(0, exit_code)

    def test_delete(self):
        user = MockUser()
        shell = TestShell(commands=[user.delete])
        exit_code = shell.run_cli_line(
            'test_shell delete --id usr_kKVqPIIdH3Ezbl1')
        self.assertEqual(0, exit_code)


if __name__ == "__main__":
    test = CommandSpecTest()
    test.setUp()
