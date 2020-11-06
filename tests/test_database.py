<<<<<<< HEAD
from dbmanager import DBManager
from unittest import TestCase

class TestDatabase(TestCase):

    def setup(self):
        dbm = DBManager()
        # count the number of users
        dbm.list_use

    def add_user(self):
        pass

    def list_users(self):
        pass

    def delete_user(self):
        pass
=======
from unittest import TestCase
from ..dbmanager import DBManager


class TestDatabase(TestCase):

    def setUp(self) -> None:
        self.dbm = DBManager()

    def test_a_add_user(self) -> None:
        # correct
        self.assertTrue(self.dbm.add_user(telegram_id=1234, user='Vicent', role='user', password=None))
        # duplicate stuff
        self.assertFalse(self.dbm.add_user(telegram_id=1234, user='Joan', role='user', password=None))
        self.assertFalse(self.dbm.add_user(telegram_id=4567, user='Vicent', role='user', password=None))

    def test_b_exist_user(self) -> None:
        self.assertTrue(self.dbm.exist_user('Vicent'))
        self.assertFalse(self.dbm.exist_user('Joan'))

    def test_c_get_user(self) -> None:
        user = self.dbm.get_user(1234)
        self.assertEqual(user[1], "Vicent")
        # inexistent
        self.assertIsNone(self.dbm.get_user(5678))

    def test_d_add_code(self) -> None:
       pass

    def test_e_delete_code(self) -> None:
        pass

    def test_f_exist_code(self) -> None:
        pass

    def test_g_list_codes(self) -> None:
        pass
>>>>>>> 0253c38ae7bc867332fcccb2eb36e52ca8dd411b
