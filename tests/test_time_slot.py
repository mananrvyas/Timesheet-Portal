import unittest
from TimeSlot import TimeSlot


class TestTimeSlot(unittest.TestCase):

    def test_time_slot_creation(self):
        slot = TimeSlot('01/01/23', '09:00', '11:00')
        self.assertEqual(slot.get_date(), '01/01/23')
        self.assertEqual(slot.get_day(), 'Sunday')
        self.assertNotEqual(slot.get_start(), slot.get_end())

    def test_duration(self):
        slot = TimeSlot('01/01/23', '09:00', '11:00')
        self.assertEqual(slot.duration(), 2)

    def test_invalid_time(self):
        with self.assertRaises(ValueError):
            TimeSlot('01/01/23', '11:00', '09:00')  # End time before start time

    def test_get_date(self):
        slot = TimeSlot('01/01/23', '09:00', '11:00')
        self.assertEqual(slot.get_date(), '01/01/23')

    def test_get_day(self):
        slot = TimeSlot('01/01/23', '09:00', '11:00')
        self.assertEqual(slot.get_day(), 'Sunday')

    def test_get_start(self):
        slot = TimeSlot('01/01/23', '09:00', '11:00')
        self.assertEqual(slot.get_start(), slot._start)
