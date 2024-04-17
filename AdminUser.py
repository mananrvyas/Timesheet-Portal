from StandardUser import StandardUser
from PayPeriod import PayPeriod
from TimeSlot import TimeSlot
import json

class AdminUser(StandardUser):
    def __init__(self, username, password, organization, default_schedule=None, timesheets=None):
        super().__init__(username, password, organization, default_schedule, timesheets)

    def approve_timesheet(self, user, pay_period):
        if pay_period in user._timesheets:
            user._timesheets[pay_period].is_approved = 'approved'
        else:
            raise ValueError("Pay period not found in user timesheets.")

    def reject_timesheet(self, user, pay_period):
        if pay_period in user._timesheets:
            user._timesheets[pay_period].is_approved = 'rejected'
        else:
            raise ValueError("Pay period not found in user timesheets.")

    def view_user_timesheets(self, user):
        return user.get_timesheets()

    def view_last_x_pay_periods(self, user, x):
        sorted_periods = sorted(user._timesheets.keys(), key=lambda pp: pp._start, reverse=True)
        return {pp: user._timesheets[pp] for pp in sorted_periods[:x]}

    @staticmethod
    def deserialize(user):
        user = json.loads(user)

        if user['default_schedule'] is None or user['default_schedule'] == {}:
            deserialized_schedule = {}
        else:
            deserialized_schedule = {day: [TimeSlot.deserialize(slot) for slot in slots]
                                     for day, slots in user['default_schedule'].items()}

        deserialized_timesheets = []

        for timesheet in user['timesheets']:
            deserialized_timesheets.append({
                'pay_period': PayPeriod(timesheet['pay_period']['start']),
                'timesheet': {date: [TimeSlot.deserialize(slot) for slot in slots] for date, slots in
                              timesheet['timesheet'].items()}
            })

        new_user = AdminUser(user['username'], user['password'], user['organization'],
                             deserialized_schedule, deserialized_timesheets)

        if 'email_address' in user:
            new_user.email_address = user['email_address']
        if 'fname' in user:
            new_user.fname = user['fname']
        if 'lname' in user:
            new_user.lname = user['lname']
        if 'photo' in user:
            new_user.photo = user['photo']
        if 'miscellaneous' in user:
            new_user.miscellaneous = user['miscellaneous']
        if 'phone_number' in user:
            new_user._phone_number = user['phone_number']

        for timesheet in deserialized_timesheets:
            pay_period = timesheet['pay_period']
            pay_period.is_approved = user['timesheets'][deserialized_timesheets.index(timesheet)]['pay_period'][
                'is_approved']
            pay_period._timesheet = timesheet['timesheet']

        return new_user
