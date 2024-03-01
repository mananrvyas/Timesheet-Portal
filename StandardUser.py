from PayPeriod import PayPeriod
from TimeSlot import TimeSlot
from datetime import datetime, timedelta, date
import hashlib
# import pandas as pd
# import matplotlib.pyplot as plt

class StandardUser:
    def __init__(self, username, password, role, organization, email_address, default_schedule=None, timesheets=[]):
        self._username = username
        self._password = password
        self._role = role
        self._default_schedule = default_schedule if default_schedule else {}
        self._timesheets = timesheets
        self._organization = organization
        self._email_address = username + '@msu.edu'
        self._fname = None
        self._lname = None
        self._photo = None
        self._miscellaneous = None
        self._phone_number = None
        # hourly wage (optional) # we can show their total earnings for the pay period

    def set_password(self, password):
        self._password = hashlib.sha256(password.encode()).hexdigest()

    def set_first_name(self, fname):
        self._fname = fname

    def set_last_name(self, lname):
        self._lname = lname

    def set_photo_url(self, photo):
        self._photo = photo

    def set_miscellaneous(self, misc):
        self._miscellaneous = misc

    def set_phone_number(self, phone):
        self._phone_number = phone

    def check_password(self, input_password):
        return self._password == hashlib.sha256(input_password.encode()).hexdigest()

    def submit_timesheet(self, pay_period, timeslots):
        if not isinstance(pay_period, PayPeriod):
            raise TypeError("pay_period must be an instance of PayPeriod")

        for i in timeslots:
            pay_period.add_timeslot(i)

        # check if pay period is already in timesheets
        for i in self._timesheets:
            if i['pay_period'] == pay_period:
                raise ValueError("Pay period already exists")

        self._timesheets.append(pay_period.get_pay_period_and_timesheet())

    def get_timesheet(self, pay_period):
        for i in self._timesheets:
            if i['pay_period'] == pay_period:
                return i['timesheet']

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
        repr = (f"Username: {self._username}\n"
                f"Role: {self._role}\n"
                f"Organization: {self._organization}\n"
                f"Default Schedule: {self._default_schedule}\n"
                f"Timesheets: {self._timesheets}\n")
        return repr

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
                'pay_period': timesheet['pay_period'],
                'timesheet': {date: [slot.serialize() for slot in slots] for date, slots in timesheet['timesheet'].items()}
            })

        return {
            'username': self._username,
            'password': self._password,
            'role': self._role,
            'organization': self._organization,
            'default_schedule': serialized_schedule,
            'timesheets': serialized_timesheets,
            'email_address': self._email_address
        }

    @staticmethod
    def deserialize(user):

        # if error in deserialize, check the line 67 in payperiod.py

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
# DEFAULT_SCHEDULE = {
#         'Sunday': [],
#         'Monday': [TimeSlot('01/03/23', '09:00', '11:00'), TimeSlot('01/03/23', '13:00', '17:00')],
#         'Tuesday': [TimeSlot('01/04/23', '09:10', '12:00'), TimeSlot('01/04/23', '14:00', '17:00')],
#         'Wednesday': [TimeSlot('01/05/23', '09:50', '12:00'), TimeSlot('01/05/23', '15:00', '17:00')],
#         'Thursday': [TimeSlot('01/06/23', '09:40', '12:00'), TimeSlot('01/06/23', '16:00', '17:00')],
#         'Friday': [TimeSlot('01/07/23', '09:30', '12:00'), TimeSlot('01/07/23', '16:30', '17:00')],
#         'Saturday': []
#     }
#
# user = StandardUser('vyasmana', hashlib.sha256('Manan'.encode()).hexdigest(), 'user', 'MSU', 'vyasmana@msu.edu',
#                      DEFAULT_SCHEDULE)
#
#
#
#
# custom_timeslots = [
#     TimeSlot('01/16/23', '10:00', '15:00'),
#     TimeSlot('01/17/23', '10:00', '15:00'),
#     TimeSlot('01/18/23', '10:00', '15:00'),
# ]
# second_pay_period = PayPeriod('01/15/23')
#
# user.submit_timesheet(second_pay_period, custom_timeslots)
#
# third_pay_period = PayPeriod('01/29/23')
# custom_timeslots = [
#     TimeSlot('01/30/23', '10:00', '15:00'),
#     TimeSlot('01/31/23', '10:00', '15:00'),
#     TimeSlot('02/01/23', '10:00', '15:00'),
# ]
# user.submit_timesheet(third_pay_period, custom_timeslots)
#
# pay_period = PayPeriod('02/11/24')
# user.submit_default_schedule(pay_period)
#
# #
# # timesheets = user.get_timesheets()
# # for i in timesheets:
# #     print(i['pay_period'])
# #     print(i['timesheet'])
#
#
# time_sheets = user._timesheets
#
# # print(time_sheets)
#
# last_five_timeshetes = []
# for i in range(5):
#     if i == 5:
#         break
#     try:
#         last_five_timeshetes.append(time_sheets[i]['pay_period'])
#     except:
#         last_five_timeshetes.append("")
#
# last_five_pay_periods = []
# for i in range(5):
#     if i == 5:
#         break
#     try:
#         last_five_pay_periods.append(last_five_timeshetes[i].get_start_date().strftime('%d %b'))
#     except:
#         last_five_pay_periods.append("")
#
#
# hours = []
# for i in range(5):
#     if i == 5:
#         break
#     try:
#         hours.append(last_five_timeshetes[i].get_total_hours())
#     except:
#         print("error")
#         hours.append(0)
#
# status = []
# for i in range(5):
#     if i == 5:
#         break
#     try:
#         status.append(last_five_timeshetes[i].is_approved)
#     except:
#         status.append('pending')
#
# data = {
#     'Date': last_five_pay_periods,
#     'Hours': hours,
#     'Status': status
# }
#
# print(data)
#
# df = pd.DataFrame(data)
#
# def plot_timesheet_bar_chart(df):
#     plt.style.use('dark_background')
#     status_colors = {'approved': 'green', 'rejected': 'red', 'pending': 'blue'}
#     colors = df['Status'].map(status_colors)
#     fig, ax = plt.subplots()
#     bars = ax.bar(df['Date'], df['Hours'], color=colors, width=0.2)
#
#     ax.set_facecolor('#0f1116')
#     fig.patch.set_facecolor('#0f1116')
#     ax.set_xlabel('Date', fontsize=12, color='white')
#     ax.set_ylabel('Hours', fontsize=12, color='white')
#     ax.tick_params(axis='x', colors='white')
#     ax.tick_params(axis='y', colors='white')
#     ax.set_ylim(0, 40)
#     ax.set_title('Timesheets', fontsize=14, color='white')
#
#     ax.xaxis.labelpad = 15
#     ax.yaxis.labelpad = 15
#
#     return fig
#
# # plot the bar chart
# fig = plot_timesheet_bar_chart(df)
# plt.show()




#
# default_schedule = {
#         'Sunday': [],
#         'Monday': [TimeSlot('01/03/23', '09:00', '12:00'), TimeSlot('01/03/23', '12:00', '17:00')],
#         'Tuesday': [TimeSlot('01/04/23', '01:00', '12:00'), TimeSlot('01/04/23', '14:00', '17:00')],
#         'Wednesday': [TimeSlot('01/05/23', '09:00', '12:00'), TimeSlot('01/05/23', '13:00', '17:00')],
#         'Thursday': [TimeSlot('01/06/23', '09:00', '12:00'), TimeSlot('01/06/23', '15:00', '17:00')],
#         'Friday': [TimeSlot('01/07/23', '09:00', '12:00'), TimeSlot('01/07/23', '16:00', '17:00')],
#         'Saturday': []
#     }

# user = StandardUser('johndoe', 'password123', 'employee', 'company','vyasmana@msu.edu', default_schedule)
# # print(user)
# print('------------------')
# # print(user.serialize())
#
# first_pay_period = PayPeriod('01/01/23')
#
# user.submit_default_schedule(first_pay_period)
#
# # print(user)
# #
# # print(user.timesheets)
# print(user.get_latest_timesheet_status())

# print(first_pay_period.is_approved)


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

