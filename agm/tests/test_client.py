from unittest import TestCase
from agm.aws import Account, InstanceSet
from agm.ssh import Client
import os

# Change this path to reflect where the .pem file is for logging into test instance
TEST_KEY = '{0}/.ssh/agm-test.pem'.format(os.environ['HOME'])

# Change this string to reflect the username for logging into the test instance
USER = 'ubuntu'

# Change this string to filter the instance set to a specific test instance
INSTANCE_ID = 'i-7bd304a7'


class TestClient(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.account = Account()
        cls.account.update_instances()
        cls.instance_set = InstanceSet('Test', cls.account)
        cls.instance_set.filter_on_names(INSTANCE_ID)
        cls.instance = cls.instance_set.instances[0]
        cls.client = Client(cls.instance.public_ip_address, TEST_KEY, USER)

    def test_send_command(self):
        resp = self.client.send_command('pwd')
        self.assertTrue(resp.stdout)
        resp = self.client.send_command('')
        self.assertFalse(resp.stdout)

    def test_send_commands_one_arg(self):
        resp = self.client.send_command('pwd')
        resp2 = self.client.send_commands('pwd')
        self.assertEqual(resp.stdout, resp2.stdout)

    def test_send_commands_multi_arg(self):
        commands = ['touch agm-test', 'ls', 'rm agm-test']
        resp = self.client.send_commands(commands)
        self.assertIn('agm-test', resp.stdout)
        self.assertNotIn('m-t', resp.stdout)
