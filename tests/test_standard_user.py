import unittest
from StandardUser import StandardUser
from PayPeriod import PayPeriod
from TimeSlot import TimeSlot


class TestStandardUser(unittest.TestCase):
    def setUp(self):
        default_schedule = {
            'Sunday': [],
            'Monday': [TimeSlot('01/03/23', '09:00', '12:00'), TimeSlot('01/03/23', '12:00', '17:00')],
            'Tuesday': [TimeSlot('01/04/23', '01:00', '12:00'), TimeSlot('01/04/23', '14:00', '17:00')],
            'Wednesday': [TimeSlot('01/05/23', '09:00', '12:00'), TimeSlot('01/05/23', '13:00', '17:00')],
            'Thursday': [TimeSlot('01/06/23', '09:00', '12:00'), TimeSlot('01/06/23', '15:00', '17:00')],
            'Friday': [TimeSlot('01/07/23', '09:00', '12:00'), TimeSlot('01/07/23', '16:00', '17:00')],
            'Saturday': []
        }

        self.user = StandardUser('johndoe', 'password', 'employee', 'ASN', default_schedule)
        self.user.set_password('password')

    def test_check_password(self):
        self.assertTrue(self.user.check_password('password'))
        self.assertFalse(self.user.check_password('wrongpassword'))

    def test_submit_default_schedule(self):
        pay_period = PayPeriod('01/01/23')

        self.user.submit_default_schedule(pay_period)

        # verify the submitted timesheet
        self.assertIn(TimeSlot('01/02/23', '09:00', '12:00'), self.user.get_timesheet(pay_period).
                      get_timesheet_by_date('01/02/23'))

        self.assertIn(TimeSlot('01/02/23', '12:00', '17:00'), self.user.get_timesheet(pay_period).
                      get_timesheet_by_date('01/02/23'))

        # get the total hours
        self.assertEqual(self.user.get_total_hours(pay_period), 76)

    def test_submit_and_retrive_timesheet(self):
        pay_period = PayPeriod('01/01/23')
        timeslot = TimeSlot('01/02/23', '09:00', '19:00')
        self.user.submit_timesheet(pay_period, [timeslot])
        # print(self.user)
        self.assertIn(timeslot, self.user.get_timesheet(pay_period).get_timesheet_by_date('01/02/23'))

    def test_total_hours(self):
        pay_period = PayPeriod('01/15/23')
        timeslot = TimeSlot('01/15/23', '09:00', '11:00')
        timeslot2 = TimeSlot('01/15/23', '12:00', '14:00')
        timeslot3 = TimeSlot('01/16/23', '15:00', '17:00')
        self.user.submit_timesheet(pay_period, [timeslot, timeslot2, timeslot3])

        self.assertEqual(self.user.get_total_hours(pay_period), 6)


if __name__ == '__main__':
    unittest.main()
