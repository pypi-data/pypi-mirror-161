# cli code
import json
# python module
from os.path import abspath, dirname
from unittest.mock import patch

# cli code
from seqslab.role.commands import BaseRole
from seqslab.role.resource.base import BaseResource

role_data_location = f'{dirname(abspath(__file__))}'
fixtures_dir = f'{role_data_location}/fixtures/'
list_resp = 'list_roles.json'


class MockResource(BaseResource):

    def list_role(self, **kwargs) -> dict:
        with open(f'{fixtures_dir}/{list_resp}', 'r') as f:
            ret = json.load(f)
        return ret


class MockRole(BaseRole):
    """
    Mock roles commands
    """
    workspace = 'test'

    def __init__(self):
        pass


role_patch = patch('seqslab.role.commands.Role', MockRole)
resource_patch = patch('seqslab.role.resource.azure.AzureResource', MockResource)

from unittest import TestCase
from seqslab.tests.util import TestShell


class BasicTest(TestCase):
    mock_command = MockRole()
    workspace = 'test'
    shell = TestShell


@role_patch
@resource_patch
class CommandSpecTest(BasicTest):

    def test_list(self):
        role = MockRole()
        shell = TestShell(commands=[role.list])
        exit_code = shell.run_cli_line(f"test_shell list")
        self.assertEqual(0, exit_code)


if __name__ == "__main__":
    test = CommandSpecTest()
    test.setUp()

