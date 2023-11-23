import unittest
from AdminUser import AdminUser


class TestAdminUser(unittest.TestCase):
    def test_admin_user(self):
        user = AdminUser()


if __name__ == '__main__':
    unittest.main()
