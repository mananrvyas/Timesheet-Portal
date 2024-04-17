from PayPeriod import PayPeriod
from TimeSlot import TimeSlot
from datetime import datetime, timedelta, date
import hashlib
import json


class StandardUser:
    def __init__(self, username, password, organization, default_schedule=None, timesheets=None):
        self.username = username
        self._password = password
        self._default_schedule = {} if default_schedule is None else default_schedule
        self._timesheets = [] if timesheets is None else timesheets
        self.organization = organization
        self.email_address = username + '@msu.edu'
        self.fname = None
        self.lname = None
        self.photo = None
        self.miscellaneous = None
        self._phone_number = None
        # hourly wage (optional) # we can show their total earnings for the pay period

    def set_password(self, password):
        self._password = password

    def set_first_name(self, fname):
        self.fname = fname

    def set_timesheets(self, timesheets):
        self._timesheets = timesheets

    def set_last_name(self, lname):
        self.lname = lname

    def set_photo_url(self, photo):
        self.photo = photo

    def set_miscellaneous(self, misc):
        self.miscellaneous = misc

    def set_phone_number(self, phone):
        self._phone_number = phone

    def check_password(self, input_password):
        return self._password == input_password

    def submit_timesheet(self, pay_period, timeslots):
        # if not isinstance(pay_period, PayPeriod):
        #     print(type(pay_period))
        #     raise TypeError(f"pay_period must be an instance of PayPeriod, not {type(pay_period)}")

        for i in timeslots:
            pay_period.add_timeslot(i)

        # check if pay period is already in timesheets
        for i in self._timesheets:
            if i['pay_period'].get_start_date() == pay_period.get_start_date():
                raise ValueError("You've already submitted a timesheet for this pay period.")

        self._timesheets.append(pay_period.get_pay_period_and_timesheet())

    def get_timesheet(self, pay_period):
        for i in self._timesheets:
            if i['pay_period'] == pay_period:
                return i['timesheet']

    def get_password(self):
        return self._password

    def get_timesheets(self):
        return self._timesheets

    def get_latest_timesheet_status(self):
        pay_period = self.get_latest_pay_period()
        return pay_period.is_approved

    def get_latest_pay_period(self):
        return self._timesheets[-1]['pay_period']

    def edit_default_schedule(self, schedule):
        self._default_schedule = schedule

    def get_total_hours(self, pay_period):
        if pay_period in self._timesheets:
            return self._timesheets[pay_period].get_total_hours()
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
            if day_name in self._default_schedule:
                for slot in self._default_schedule[day_name]:
                    new_slot = TimeSlot(current_date.strftime('%m/%d/%y'), slot.get_start().strftime('%H:%M'),
                                        slot.get_end().strftime('%H:%M'))
                    timeslots.append(new_slot)
            current_date += timedelta(days=1)

        self.submit_timesheet(pay_period, timeslots)

    def __repr__(self):
        repr = (f"Username: {self.username}\n"
                f"Organization: {self.organization}\n"
                f"Default Schedule: {self._default_schedule}\n"
                f"Timesheets: {self._timesheets}\n"
                f"Email Address: {self.email_address}\n"
                f"First Name: {self.fname}\n"
                f"Last Name: {self.lname}\n"
                f"Photo: {self.photo}\n"
                f"Miscellaneous: {self.miscellaneous}\n"
                f"Phone Number: {self._phone_number}\n")
        return repr

    def __eq__(self, other):
        if not isinstance(other, StandardUser):
            return NotImplemented
        return (self.username, self._password, self.organization, self._default_schedule, self._timesheets,
                self.email_address, self.fname, self.lname, self.photo, self.miscellaneous, self._phone_number) == \
               (other.username, other._password, other.organization, other._default_schedule, other._timesheets,
                other.email_address, other.fname, other.lname, other.photo, other.miscellaneous, other._phone_number)

    def serialize_schedule(self):
        serialized_schedule = {day: [slot.serialize() for slot in slots]
                               for day, slots in self._default_schedule.items()}
        return serialized_schedule

    @staticmethod
    def deserialize_schedule(schedule):
        deserialized_schedule = {day: [TimeSlot.deserialize(slot) for slot in slots]
                                 for day, slots in schedule.items()}
        return deserialized_schedule

    def serialize(self):
        serialized_schedule = {day: [slot.serialize() for slot in slots]
                               for day, slots in self._default_schedule.items()}
        serialized_timesheets = []

        for timesheet in self._timesheets:
            serialized_timesheets.append({
                'pay_period': {
                    'start': timesheet['pay_period'].get_start_date().strftime('%m/%d/%y'),
                    'is_approved': timesheet['pay_period'].is_approved
                },
                'timesheet': {date: [slot.serialize() for slot in slots] for date, slots in
                              timesheet['timesheet'].items()}
            })

        return json.dumps({
            'username': self.username,
            'password': self._password,
            'organization': self.organization,
            'default_schedule': serialized_schedule,
            'timesheets': serialized_timesheets,
            'email_address': self.email_address,
            'fname': self.fname,
            'lname': self.lname,
            'photo': self.photo,
            'miscellaneous': self.miscellaneous,
            'phone_number': self._phone_number
        })

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

        new_user = StandardUser(user['username'], user['password'], user['organization'],
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


# new_user = StandardUser('manan', 'password', 'organization')
#
