from datetime import datetime
# from PayPeriod import PayPeriod
import json


class TimeSlot:
    def __init__(self, date, start, end):
        self._date = datetime.strptime(date, '%m/%d/%y')
        self._start = datetime.strptime(f"{date} {start}", '%m/%d/%y %H:%M')
        self._day = self._date.strftime('%A')
        self._end = datetime.strptime(f"{date} {end}", '%m/%d/%y %H:%M')
        if self._start >= self._end:
            raise ValueError("Start time must be before end time.")

    def duration(self):
        return round(((self._end - self._start).seconds / 3600), 1)

    def get_date(self):
        return self._date.strftime('%m/%d/%y')

    def __repr__(self):
        # day, data, start, end, duration
        return f"{self._date.strftime('%m/%d/%y')}, {self._start.strftime('%H:%M')}, " \
               f"{self._end.strftime('%H:%M')}"

    def __eq__(self, other):
        if not isinstance(other, TimeSlot):
            return NotImplemented
        return (self._date, self._start, self._end) == (other._date, other._start, other._end)

    def __hash__(self):
        return hash((self._date, self._start, self._end))

    def get_day(self):
        return self._day

    def get_start(self):
        return self._start

    def get_end(self):
        return self._end

    def serialize(self):
        return {
            'date': self._date.strftime('%m/%d/%y'),
            'start': self._start.strftime('%H:%M'),
            'end': self._end.strftime('%H:%M'),
        }

    @staticmethod
    def deserialize(timeslot):
        return TimeSlot(timeslot['date'], timeslot['start'], timeslot['end'])

# test_slot = TimeSlot('12/3/23', '10:00', '9:00')
# test_slot_2 = TimeSlot('12/3/23', '12:00', '14:00')
# pay_period = PayPeriod('12/3/23', {'12/03/23': [test_slot, test_slot_2]})
# # print(pay_period.contains(test_slot.get_date()))
# #
# # pay_period.add_timeslot(test_slot)
# # test_slot_2 = TimeSlot('12/3/23', '12:00', '14:00')
# pay_period.add_timeslot(test_slot_2)
# print(pay_period.get_timesheet_by_date('12/03/23'))
# print(pay_period.get_timesheet_by_pay_period())
# print(pay_period.get_total_hours())
