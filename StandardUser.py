class StandardUser:
    def __init__(self, username, password, role, default_schedule):
        self.username = username
        self.password = password
        self.role = role
        self.default_schedule = default_schedule
        self.timesheets = {}

    def check_password(self, password):
        # NO HASHING YET
        return self.password == password

    def submit_timesheet(self, pay_period, schedule):
        # add the timesheet to the database
        self.timesheets[pay_period] = schedule

    def get_timesheet(self, pay_period):
        # return the timesheet from the database
        if self.timesheets.get(pay_period) is None:
            return "No timesheet found for this pay period"
        else:
            return self.timesheets[pay_period]

    def get_timesheets(self):
        # return all the timesheets from the database and add it to the list
        return self.timesheets




