from unittest import TestCase
from agm.account import Account, InstanceSet


account = None


def setUpModule():
    global account
    account = Account()


class TestAccount(TestCase):

    def test_should_be_true(self):
        self.assertTrue(True)

    def test_update_instances(self):
        self.assertEqual(len(account), 0)
        account.update_instances()
        self.assertGreater(len(account), 0)
        # If this fails, check that you have at least one instance to query


class TestInstanceSet(TestCase):

    def setUp(self):
        self.i_set = InstanceSet('all', account)

    def test_names(self):
        self.assertGreater(len(self.i_set.get_names()), 0)
        self.assertIsInstance(self.i_set.get_names(), list)
        self.assertIsInstance(self.i_set.get_names()[0], str)

    def test_ids(self):
        self.assertGreater(len(self.i_set.get_ids()), 0)
        self.assertIsInstance(self.i_set.get_ids(), list)
        self.assertIsInstance(self.i_set.get_ids()[0], str)

    def test_filter_on_names_blacklist(self):
        names = self.i_set.get_names()
        self.i_set.filter_on_names(names[:2])
        new_names = self.i_set.get_names()
        self.assertEqual(len(names) - len(new_names), 2)

    def test_filter_on_names_whitelist(self):
        names = self.i_set.get_names()
        self.i_set.filter_on_names(names[:2], mode='whitelist')
        new_names = self.i_set.get_names()
        self.assertEqual(len(new_names), 2)

    def test_filter_on_name_string_caught(self):
        names = self.i_set.get_names()
        badname = names[0] * 8
        self.i_set.filter_on_names(badname)
        new_names = self.i_set.get_names()
        self.assertEqual(len(names), len(new_names))

    def test_filter_on_ids_blacklist(self):
        ids = self.i_set.get_ids()
        self.i_set.filter_on_ids(ids[:2])
        new_ids = self.i_set.get_ids()
        self.assertEqual(len(ids) - len(new_ids), 2)

    def test_filter_on_ids_whitelist(self):
        ids = self.i_set.get_ids()
        self.i_set.filter_on_ids(ids[:2], mode='whitelist')
        new_ids = self.i_set.get_ids()
        self.assertEqual(len(new_ids), 2)
