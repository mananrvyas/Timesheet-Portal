import unittest
from tests.test_standard_user import TestStandardUser
from tests.test_admin_user import TestAdminUser


def suite():
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestStandardUser))
    suite.addTests(loader.loadTestsFromTestCase(TestAdminUser))

    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
