import unittest
from AdminUser import AdminUser
from StandardUser import StandardUser
from PayPeriod import PayPeriod
from TimeSlot import TimeSlot


class TestAdminUser(unittest.TestCase):
    def setUp(self):
        self.admin = AdminUser('adminuser', 'adminpass', 'admin', 'company')
        self.user = StandardUser('johndoe', 'password123', 'employee', 'company')
        self.pay_period = PayPeriod('01/01/23')

    def test_approve_timesheet(self):
        self.user.submit_default_schedule(self.pay_period)
        self.admin.approve_timesheet(self.user, self.pay_period)
        self.assertEqual(self.user.get_timesheet(self.pay_period).is_approved, 'approved')

    def test_view_user_timesheets(self):
        self.user.submit_default_schedule(self.pay_period)
        timesheets = self.admin.view_user_timesheets(self.user)
        self.assertIn(self.pay_period, timesheets)

    def test_view_last_x_pay_periods(self):
        second_pay_period = PayPeriod('01/15/23')
        self.user.submit_default_schedule(self.pay_period)
        self.user.submit_default_schedule(second_pay_period)
        last_timesheets = self.admin.view_last_x_pay_periods(self.user, 1)
        self.assertIn(second_pay_period, last_timesheets)


if __name__ == '__main__':
    unittest.main()
