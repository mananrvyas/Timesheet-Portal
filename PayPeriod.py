from datetime import datetime, timedelta
from TimeSlot import TimeSlot


class PayPeriod:
    def __init__(self, start_date, timesheet=None):
        if timesheet is None:
            timesheet = {}
        self._start = datetime.strptime(start_date, '%m/%d/%y')
        if self._start.strftime('%A') != 'Sunday':
            raise ValueError("Pay period must start on a Sunday")
        self._end = self._start + timedelta(days=13)  # 14 days
        self._timesheet = timesheet
        self.is_approved = "pending"

    def contains(self, date):
        date = datetime.strptime(date, '%m/%d/%y')
        return self._start <= date <= self._end

    def add_timeslot(self, timeslot):
        date = timeslot.get_date()
        if not self.contains(date):
            raise ValueError("Incorrect pay period")

        # Check for overlapping timeslots
        if self._timesheet.get(date) is not None:
            for slot in self._timesheet[date]:
                if (slot.get_start() < timeslot.get_start() < slot.get_end() or
                        slot.get_start() < timeslot.get_end() < slot.get_end()):
                    raise ValueError("Overlapping timeslots")

        if self._timesheet.get(date) is None:
            self._timesheet[date] = [timeslot]
        else:
            self._timesheet[date].append(timeslot)

    def get_timesheet_by_date(self, date):
        return self._timesheet.get(date, None)

    def get_timesheet_by_pay_period(self):
        return self._timesheet

    def get_total_hours(self):
        total_hours = 0
        for date in self._timesheet:
            for timeslot in self._timesheet[date]:
                total_hours += timeslot.duration()
        return total_hours

    def get_start_date(self):
        return self._start

    def approve(self):
        self.is_approved = "approved"

    def reject(self):
        self.is_approved = "rejected"

    def __repr__(self):
        # start, end, timesheet
        return f"{self._start.strftime('%m/%d/%y')}"

    def get_pay_period_and_timesheet(self):
        return {'pay_period': self._start.strftime('%m/%d/%y'), 'timesheet': self._timesheet}

    def serialize(self):
        return {
            'start': self._start.strftime('%m/%d/%y'),
            'timesheet': {date: [slot.serialize() for slot in slots] for date, slots in self._timesheet.items()},
            'is_approved': self.is_approved,
        }

    @staticmethod
    def deserialize(pay_period):
        return PayPeriod(pay_period['start'], {date: [TimeSlot.deserialize(slot) for slot in slots] for date, slots in pay_period['timesheet'].items()})


# first_pay_period = PayPeriod('01/01/23')
# custom_timeslots = [
#     TimeSlot('01/02/23', '10:00', '15:00'),
#     TimeSlot('01/03/23', '10:00', '15:00'),
#     TimeSlot('01/04/23', '10:00', '15:00'),
# ]
# for i in custom_timeslots:
#     first_pay_period.add_timeslot(i)

# zz = first_pay_period.serialize()
# print(zz)
# print(first_pay_period.get_timesheet_by_pay_period())
#
# new_zz = PayPeriod.deserialize(zz)
# print(new_zz.get_timesheet_by_pay_period())
