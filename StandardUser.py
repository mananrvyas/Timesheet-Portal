from PayPeriod import PayPeriod
from TimeSlot import TimeSlot
from datetime import datetime, timedelta
import hashlib


class StandardUser:
    def __init__(self, username, password, role, organization, email_address, default_schedule=None, timesheets=[]):
        self.username = username
        self.password = password
        self.role = role
        self.default_schedule = default_schedule if default_schedule else {}
        self.timesheets = timesheets
        self.organization = organization
        self.email_address = email_address
        # hourly wage (optional) # we can show their total earnings for the pay period

    def set_password(self, password):
        self.password = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, input_password):
        return self.password == hashlib.sha256(input_password.encode()).hexdigest()

    def submit_timesheet(self, pay_period, timeslots):
        if not isinstance(pay_period, PayPeriod):
            raise TypeError("pay_period must be an instance of PayPeriod")

        for i in timeslots:
            pay_period.add_timeslot(i)

        self.timesheets.append(pay_period.get_pay_period_and_timesheet())

    def get_timesheet(self, pay_period):
        for i in self.timesheets:
            if i['pay_period'] == pay_period:
                return i['timesheet']

    def get_timesheets(self):
        return self.timesheets

    def edit_default_schedule(self, schedule):
        self.default_schedule = schedule

    def get_total_hours(self, pay_period):
        if pay_period in self.timesheets:
            return self.timesheets[pay_period].get_total_hours()
        else:
            return 0

    def submit_default_schedule(self, pay_period):
        if not isinstance(pay_period, PayPeriod):
            raise TypeError("pay_period must be an instance of PayPeriod")

        if not pay_period.get_start_date().strftime('%A') == 'Sunday':
            raise ValueError("Pay period must start on a Sunday")

        timeslots = []
        current_date = pay_period.get_start_date()

        for i in range(14):  # 14 days in a pay period
            day_name = current_date.strftime('%A')
            if day_name in self.default_schedule:
                for slot in self.default_schedule[day_name]:
                    new_slot = TimeSlot(current_date.strftime('%m/%d/%y'), slot.get_start().strftime('%H:%M'),
                                        slot.get_end().strftime('%H:%M'))
                    timeslots.append(new_slot)
            current_date += timedelta(days=1)

        self.submit_timesheet(pay_period, timeslots)

    def __repr__(self):
        repr = (f"Username: {self.username}\n"
                f"Role: {self.role}\n"
                f"Organization: {self.organization}\n"
                f"Default Schedule: {self.default_schedule}\n"
                f"Timesheets: {self.timesheets}\n")
        return repr

    def serialize_schedule(self):
        serialized_schedule = {day: [slot.serialize() for slot in slots]
                               for day, slots in self.default_schedule.items()}
        return serialized_schedule

    @staticmethod
    def deserialize_schedule(schedule):
        deserialized_schedule = {day: [TimeSlot.deserialize(slot) for slot in slots]
                                 for day, slots in schedule.items()}
        return deserialized_schedule

    def serialize(self):
        serialized_schedule = {day: [slot.serialize() for slot in slots]
                               for day, slots in self.default_schedule.items()}
        serialized_timesheets = []

        for timesheet in self.timesheets:
            serialized_timesheets.append({
                'pay_period': timesheet['pay_period'],
                'timesheet': {date: [slot.serialize() for slot in slots] for date, slots in timesheet['timesheet'].items()}
            })

        return {
            'username': self.username,
            'password': self.password,
            'role': self.role,
            'organization': self.organization,
            'default_schedule': serialized_schedule,
            'timesheets': serialized_timesheets,
            'email_address': self.email_address
        }

    @staticmethod
    def deserialize(user):
        deserialized_schedule = {day: [TimeSlot.deserialize(slot) for slot in slots]
                                 for day, slots in user['default_schedule'].items()}

        deserialized_timesheets = []

        for timesheet in user['timesheets']:
            deserialized_timesheets.append({
                'pay_period': timesheet['pay_period'],
                'timesheet': {date: [TimeSlot.deserialize(slot) for slot in slots] for date, slots in timesheet['timesheet'].items()}
            })

        return StandardUser(user['username'], user['password'], user['role'], user['organization'], user['email_address'],
                            deserialized_schedule, deserialized_timesheets)
#
default_schedule = {
        'Sunday': [],
        'Monday': [TimeSlot('01/03/23', '09:00', '12:00'), TimeSlot('01/03/23', '12:00', '17:00')],
        'Tuesday': [TimeSlot('01/04/23', '01:00', '12:00'), TimeSlot('01/04/23', '14:00', '17:00')],
        'Wednesday': [TimeSlot('01/05/23', '09:00', '12:00'), TimeSlot('01/05/23', '13:00', '17:00')],
        'Thursday': [TimeSlot('01/06/23', '09:00', '12:00'), TimeSlot('01/06/23', '15:00', '17:00')],
        'Friday': [TimeSlot('01/07/23', '09:00', '12:00'), TimeSlot('01/07/23', '16:00', '17:00')],
        'Saturday': []
    }

# user = StandardUser('johndoe', 'password123', 'employee', 'company', default_schedule)
# print(user)
# print('------------------')
# print(user.serialize())
#
# first_pay_period = PayPeriod('01/01/23')
#
# user.submit_default_schedule(first_pay_period)
# print(user)
# print('------------------')
# print(user.serialize())
# second_pay_period = PayPeriod('01/15/23')
# custom_timeslots = [
#     TimeSlot('01/16/23', '10:00', '15:00'),
#     TimeSlot('01/17/23', '10:00', '15:00'),
#     TimeSlot('01/18/23', '10:00', '15:00'),
# ]
# user.submit_timesheet(second_pay_period, custom_timeslots)
# print(user)
# print('------------------')
# print(user.serialize())
# print('------------------')
# print(StandardUser.deserialize(user.serialize()))
#
# print(user)
#
# new_user = user.serialize()
# # for i, j in new_user.items():
# #     print(i, "::: ", j)
# # print(type(new_user))
# print(StandardUser.deserialize(new_user))
#
# # all_timeshet = user.get_timesheets()
# #
# # for i in all_timeshet:
# #     print(i['pay_period'])
# #     print(i['timesheet'])
#


# default_schedule = {
#         'Sunday': [],
#         'Monday': [TimeSlot('01/03/23', '09:00', '12:00'), TimeSlot('01/03/23', '13:00', '17:00')],
#         'Tuesday': [TimeSlot('01/04/23', '09:00', '12:00'), TimeSlot('01/04/23', '13:00', '17:00')],
#         'Wednesday': [TimeSlot('01/05/23', '09:00', '12:00'), TimeSlot('01/05/23', '13:00', '17:00')],
#         'Thursday': [TimeSlot('01/06/23', '09:00', '12:00'), TimeSlot('01/06/23', '13:00', '17:00')],
#         'Friday': [TimeSlot('01/07/23', '09:00', '12:00'), TimeSlot('01/07/23', '13:00', '17:00')],
#         'Saturday': []
#     }
# user = StandardUser('johndoe', 'password123', 'employee', 'company', default_schedule)
#
# zz = user.serialize_schedule()
#
# print(zz)
# first_pay_period = PayPeriod('01/01/23')
# user.submit_default_schedule(first_pay_period)
#
#
# second_pay_period = PayPeriod('01/15/23')
# custom_timeslots = [
#     TimeSlot('01/16/23', '10:00', '15:00'),
#     TimeSlot('01/17/23', '10:00', '15:00'),
#     TimeSlot('01/17/23', '15:00', '16:00'),
#     TimeSlot('01/18/23', '10:00', '15:00'),
# ]
# user.submit_timesheet(second_pay_period, custom_timeslots)

# for i in user.get_timesheets():
#     print(i)
#     # print("\n\n\n")

