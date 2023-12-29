import unittest
from PayPeriod import PayPeriod
from TimeSlot import TimeSlot


class TestPayPeriod(unittest.TestCase):
    def test_pay_period_creation_and_validation(self):
        pay_period = PayPeriod('01/01/23')
        self.assertEqual(pay_period.get_start_date().strftime('%m/%d/%y'), '01/01/23')
        with self.assertRaises(ValueError):
            PayPeriod('01/02/23')  # Not a Sunday

    def test_adding_and_retrieving_time_slot(self):
        pay_period = PayPeriod('01/01/23')
        slot = TimeSlot('01/02/23', '09:00', '11:00')
        pay_period.add_timeslot(slot)
        slot2 = TimeSlot('01/02/23', '08:00', '9:00')
        pay_period.add_timeslot(slot2)
        self.assertIn(slot, pay_period.get_timesheet_by_date('01/02/23'))

    def test_pay_period_start_day(self):
        with self.assertRaises(ValueError):
            PayPeriod('01/02/23')  # Not a Sunday

    def test_overlapping_timeslots(self):
        period = PayPeriod('01/01/23')
        slot1 = TimeSlot('01/02/23', '09:00', '11:00')
        slot2 = TimeSlot('01/02/23', '10:00', '12:00')  # Overlaps with slot1
        period.add_timeslot(slot1)
        with self.assertRaises(ValueError):
            period.add_timeslot(slot2)

    def test_total_hours(self):
        period = PayPeriod('01/01/23')
        slot = TimeSlot('01/02/23', '09:00', '11:00')
        period.add_timeslot(slot)
        self.assertEqual(period.get_total_hours(), 2)

    def test_add_invalid_timeslot(self):
        pay_period = PayPeriod('01/01/23')
        timeslot = TimeSlot('01/20/23', '09:00', '11:00')
        with self.assertRaises(ValueError):
            pay_period.add_timeslot(timeslot)


if __name__ == '__main__':
    unittest.main()
