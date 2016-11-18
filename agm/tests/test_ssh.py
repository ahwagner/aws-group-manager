from unittest import TestCase
from agm.aws import Account, InstanceSet
from agm.ssh import Client, DEFAULT_ERROR_LOGFILE, DEFAULT_OUTPUT_LOGFILE
import os
from pathlib import Path

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
        cls.instance_set.filter_on_ids(INSTANCE_ID, mode='whitelist')
        cls.instance = cls.instance_set.instances[0]
        cls.initial_state = 'running'
        if cls.instance.state['Name'] != 'running':
            cls.initial_state = cls.instance.state['Name']
            cls.instance.start()
            cls.instance.wait_until_running()
        cls.client = Client(cls.instance.public_ip_address, TEST_KEY, USER)

    @classmethod
    def tearDownClass(cls):
        if cls.initial_state != 'running':
            cls.client.close()
            cls.instance.stop()
            os.remove(DEFAULT_ERROR_LOGFILE)
            os.remove(DEFAULT_OUTPUT_LOGFILE)

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

    def test_command_log(self):
        p_out = Path(DEFAULT_OUTPUT_LOGFILE)
        p_out.touch()
        p_err = Path(DEFAULT_ERROR_LOGFILE)
        p_err.touch()
        stat_out_1 = os.stat(str(p_out))
        stat_err_1 = os.stat(str(p_err))
        self.client.send_command('pwd', log=True)
        self.client.send_command('pwd 1>&2', log=True)
        stat_out_2 = os.stat(str(p_out))
        stat_err_2 = os.stat(str(p_err))
        self.assertNotEqual(stat_out_1, stat_out_2)
        self.assertNotEqual(stat_err_1, stat_err_2)
