import unittest
from tests.test_standard_user import TestStandardUser
from tests.test_admin_user import TestAdminUser
from tests.test_pay_period import TestPayPeriod
from tests.test_time_slot import TestTimeSlot


def suite():
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()

    test_suite.addTests(loader.loadTestsFromTestCase(TestStandardUser))
    test_suite.addTests(loader.loadTestsFromTestCase(TestAdminUser))
    test_suite.addTests(loader.loadTestsFromTestCase(TestPayPeriod))
    test_suite.addTests(loader.loadTestsFromTestCase(TestTimeSlot))

    return test_suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
