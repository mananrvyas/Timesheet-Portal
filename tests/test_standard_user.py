import unittest
from StandardUser import StandardUser


class TestStandardUser(unittest.TestCase):
    def test_standard_user_init(self):
        user = StandardUser('Manan', '1234', 'standard',
                            {'monday': '5', 'tuesday': '7', 'wednesday': '9'})

        # testing the username, password, role, default_schedule, timesheets

        self.assertEqual(user.username, 'Manan')
        self.assertIsNot(user.username, 'manan')

        self.assertEqual(user.password, '1234')
        self.assertIsNot(user.password, '12345')

        self.assertEqual(user.role, 'standard')
        self.assertIsNot(user.role, 'admin')

        self.assertEqual(user.default_schedule, {'monday': '5', 'tuesday': '7', 'wednesday': '9'})
        self.assertIsNot(user.default_schedule, {'monday': '5', 'tuesday': '7', 'wednesday': '10'})

        self.assertEqual(user.timesheets, {})

    def test_check_passwords(self):
        user = StandardUser('Manan', '1234', 'standard',
                            {'monday': '5', 'tuesday': '7', 'wednesday': '9'})

        self.assertTrue(user.check_password('1234'))
        self.assertFalse(user.check_password('12345'))

    def test_submit_timesheet(self):
        user = StandardUser('Manan', '1234', 'standard',
                            {'monday': '5', 'tuesday': '7', 'wednesday': '9'})

        self.assertEqual(user.timesheets, {})

        user.submit_timesheet('12-10 to 12-24', user.default_schedule)

        self.assertEqual(user.timesheets, {'12-10 to 12-24': {'monday': '5', 'tuesday': '7', 'wednesday': '9'}})

    def test_get_timesheet(self):
        user = StandardUser('Manan', '1234', 'standard',
                            {'monday': '8', 'tuesday': '7', 'wednesday': '9'})

        user.submit_timesheet('12-10 to 12-24', user.default_schedule)

        self.assertEqual(user.get_timesheet('12-10 to 12-24'), {'monday': '8', 'tuesday': '7', 'wednesday': '9'})
        self.assertEqual(user.get_timesheet('12-10 to 12-25'), 'No timesheet found for this pay period')

    def test_get_timesheets(self):
        user = StandardUser('Manan', '1234', 'standard',
                            {'monday': '8', 'tuesday': '7', 'wednesday': '9'})

        user.submit_timesheet('12-10 to 12-17', user.default_schedule)
        user.submit_timesheet('12-17 to 12-24', {'monday': '8', 'tuesday': '7', 'wednesday': '9'})

        self.assertEqual(user.get_timesheets(), {'12-10 to 12-17': {'monday': '8', 'tuesday': '7', 'wednesday': '9'},
                                                 '12-17 to 12-24': {'monday': '8', 'tuesday': '7', 'wednesday': '9'}})


if __name__ == '__main__':
    unittest.main()
