from StandardUser import StandardUser
from PayPeriod import PayPeriod
from TimeSlot import TimeSlot


class AdminUser(StandardUser):
    def __init__(self, username, password, role, organization):
        super().__init__(username, password, role, organization)

    def approve_timesheet(self, user, pay_period):
        if pay_period in user._timesheets:
            user._timesheets[pay_period].is_approved = 'approved'
        else:
            raise ValueError("Pay period not found in user timesheets.")

    def view_user_timesheets(self, user):
        return user.get_timesheets()

    def view_last_x_pay_periods(self, user, x):
        sorted_periods = sorted(user._timesheets.keys(), key=lambda pp: pp._start, reverse=True)
        return {pp: user._timesheets[pp] for pp in sorted_periods[:x]}


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
# admin = AdminUser('adminuser', 'adminpass', 'admin', 'company')
#
# # Submitting timesheets for the user
# first_pay_period = PayPeriod('01/01/23')
# user.submit_default_schedule(first_pay_period)
#
# second_pay_period = PayPeriod('01/15/23')
# custom_timeslots = [
#     TimeSlot('01/16/23', '10:00', '15:00'),
#     TimeSlot('01/17/23', '10:00', '15:00'),
#     TimeSlot('01/18/23', '10:00', '15:00'),
# ]
# user.submit_timesheet(second_pay_period, custom_timeslots)
#
# # Admin approving the first pay period timesheet
# admin.approve_timesheet(user, first_pay_period)
#
# # Printing all timesheets of the user
# print("All User Timesheets:")
# for pay_period, timesheet in admin.view_user_timesheets(user).items():
#     print(f"Pay Period: {pay_period}, Approved: {timesheet.is_approved}")
#     for date, slots in timesheet.get_timesheet_by_pay_period().items():
#         print(f"  {date}:")
#         for slot in slots:
#             print(f"    {slot}")
#
# # Printing the last pay period timesheet
# print("\nLast Pay Period Timesheet:")
# last_timesheet = admin.view_last_x_pay_periods(user, 1)
# for pay_period, timesheet in last_timesheet.items():
#     print(f"Pay Period: {pay_period}, Approved: {timesheet.is_approved}")
#     for date, slots in timesheet.get_timesheet_by_pay_period().items():
#         print(f"  {date}:")
#         for slot in slots:
#             print(f"    {slot}")