from PayPeriod import PayPeriod
from TimeSlot import TimeSlot
from datetime import datetime, timedelta
import hashlib


class StandardUser:
    def __init__(self, username, password, role, organization, default_schedule=None):
        self.username = username
        self.password = password
        self.role = role
        self.default_schedule = default_schedule if default_schedule else {}
        self.timesheets = dict()
        self.organization = organization
        # hourly wage (optional) # we can show their total earnings for the pay period

    def set_password(self, password):
        self.password = hashlib.sha256(password.encode()).hexdigest()

    def check_password(self, input_password):
        return self.password == hashlib.sha256(input_password.encode()).hexdigest()

    def submit_timesheet(self, pay_period, timeslots):
        if not isinstance(pay_period, PayPeriod):
            raise TypeError("pay_period must be an instance of PayPeriod")

        if pay_period in self.timesheets:
            for timeslot in timeslots:
                self.timesheets[pay_period].add_timeslot(timeslot)
        else:
            self.timesheets[pay_period] = pay_period
            for timeslot in timeslots:
                self.timesheets[pay_period].add_timeslot(timeslot)

    def get_timesheet(self, pay_period):
        return self.timesheets.get(pay_period, None)

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
        repr = (f"Username: {self.username}\n "
                f"Role: {self.role}\n"
                f"Organization: {self.organization}\n"
                f"Default Schedule: {self.default_schedule}\n"
                f"Timesheets: {self.timesheets}\n")
        return repr

#
# def main():
#     # Create a default schedule for a user
#     default_schedule = {
#         'Sunday': [],
#         'Monday': [TimeSlot('01/03/23', '09:00', '12:00'), TimeSlot('01/03/23', '12:00', '17:00')],
#         'Tuesday': [TimeSlot('01/04/23', '01:00', '12:00'), TimeSlot('01/04/23', '14:00', '17:00')],
#         'Wednesday': [TimeSlot('01/05/23', '09:00', '12:00'), TimeSlot('01/05/23', '13:00', '17:00')],
#         'Thursday': [TimeSlot('01/06/23', '09:00', '12:00'), TimeSlot('01/06/23', '15:00', '17:00')],
#         'Friday': [TimeSlot('01/07/23', '09:00', '12:00'), TimeSlot('01/07/23', '16:00', '17:00')],
#         'Saturday': []
#     }
#
#     # Create a StandardUser
#     user = StandardUser('johndoe', 'password123', 'employee', 'company', default_schedule)
#
#     # First pay period - Using default schedule
#     first_pay_period = PayPeriod('01/15/23')
#     user.submit_default_schedule(first_pay_period)
#
#     print(user.get_timesheets())
#     print(user.get_timesheet(first_pay_period))
    #
    # # Second pay period - Submitting a custom timesheet
    # second_pay_period = PayPeriod('01/15/23')
    # custom_timeslots = [
    #     TimeSlot('01/16/23', '10:00', '15:00'),  # Custom timeslots for the second pay period
    #     TimeSlot('01/17/23', '10:00', '15:00'),
    #     TimeSlot('01/18/23', '10:00', '15:00'),
    # ]
    # user.submit_timesheet(second_pay_period, custom_timeslots)
    #
    # print(user)
    #
    # print(type(user.get_timesheet(first_pay_period)))
    #
    # # Retrieve and print all submitted timesheets
    # print(f"All timesheets for {user.username}:")
    # for pay_period, timesheet in user.get_timesheets().items():
    #     print(f"Pay Period: {pay_period}")
    #     for date, slots in timesheet.get_timesheet_by_pay_period().items():
    #         print(f"  {date}:")
    #         for slot in slots:
    #             print(f"    {slot}")
    #
    # print(f"Total hours for first pay period: {user.get_total_hours(first_pay_period)}")
    # print(f"Total hours for second pay period: {user.get_total_hours(second_pay_period)}")


if __name__ == "__main__":
    main()


