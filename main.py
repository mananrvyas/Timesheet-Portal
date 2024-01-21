from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import hashlib
from StandardUser import StandardUser
from TimeSlot import TimeSlot
from datetime import datetime, timedelta
from PayPeriod import PayPeriod

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Temporary database
USERS = [
    ['user1', hashlib.sha256('password1'.encode()).hexdigest(), 'admin', 'org1'],
    ['user2', hashlib.sha256('password2'.encode()).hexdigest(), 'user', 'org2']
]

DEFAULT_SCHEDULE = {
    'Sunday': [],
    'Monday': [TimeSlot('01/03/23', '09:00', '12:00'), TimeSlot('01/03/23', '13:00', '17:00')],
    'Tuesday': [TimeSlot('01/04/23', '09:00', '12:00'), TimeSlot('01/04/23', '13:00', '17:00')],
    'Wednesday': [TimeSlot('01/05/23', '09:00', '12:00'), TimeSlot('01/05/23', '13:00', '17:00')],
    'Thursday': [TimeSlot('01/06/23', '09:00', '12:00'), TimeSlot('01/06/23', '13:00', '17:00')],
    'Friday': [TimeSlot('01/07/23', '09:00', '12:00'), TimeSlot('01/07/23', '13:00', '17:00')],
    'Saturday': []
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    user = next((u for u in USERS if u[0] == username and u[1] == hashed_password), None)
    if user:
        session['username'] = username
        return redirect(url_for('user_home'))
    else:
        flash('Invalid username or password')
        return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        organization = request.form['organization']
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Check if username already exists
        if next((u for u in USERS if u[0] == username), None):
            flash('Username already exists')
            return redirect(url_for('signup'))

        USERS.append([username, hashed_password, role, organization])
        flash('Account created successfully')
        return redirect(url_for('index'))

    return render_template('signup.html')


@app.route('/home')
def home():
    if 'username' not in session:
        return redirect(url_for('index'))
    return 'Welcome to the Home Page'


@app.route('/user_home')
def user_home():
    if 'username' not in session:
        return redirect(url_for('index'))
    username = session['username']
    # Assuming you have a function `get_user_by_username` that retrieves the user object
    user = get_user_by_username(username)
    if user is None:
        return redirect(url_for('index'))  # Redirect if user not found
    # Ensure user is a dictionary with a 'default_schedule' key
    user_info = user  # Assuming 'serialize' method returns all user info as a dictionary
    # print(user_info)
    # user_info = StandardUser.deserialize(user_info)
    return render_template('user_home.html', user=user_info)


def get_user_by_username(username):
    return StandardUser(username, 'password123', 'employee', 'company', DEFAULT_SCHEDULE)


@app.route('/edit_schedule', methods=['POST'])
def edit_schedule():
    username = session.get('username')
    if not username:
        flash('You must be logged in to edit the schedule.')
        return redirect(url_for('index'))

    # Find the user in the USERS list
    user = get_user_by_username(username)
    if user is None:
        flash('User not found.')
        return redirect(url_for('user_home'))

    # Update the default schedule with the provided timeslots
    for day in ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']:
        # Assuming each day can have multiple timeslots
        day_timeslots = []
        for i in range(1, 4):  # Let's assume up to 3 time slots can be specified per day
            start_key = f'{day.lower()}-{i}-start'
            end_key = f'{day.lower()}-{i}-end'
            if start_key in request.form and end_key in request.form:
                start_time = request.form[start_key]
                end_time = request.form[end_key]
                if start_time and end_time:
                    # placeholder date
                    timeslot = TimeSlot('01/01/01', start_time, end_time)
                    day_timeslots.append(timeslot)
        # Now we update the user's default schedule for the day
        DEFAULT_SCHEDULE[day] = day_timeslots

    print(user)

    flash('Schedule updated successfully.')
    return redirect(url_for('user_home'))


@app.route('/delete_timeslot', methods=['POST'])
def delete_timeslot():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'User not logged in'})

    day = request.form.get('day')
    slot_index = request.form.get('slot_index', type=int)

    # Logic to delete the timeslot from the user's default schedule
    user = get_user_by_username(username)
    if user is None:
        return jsonify({'success': False, 'message': 'User not found'})

    # Assuming the user's default schedule is stored in a dictionary format
    if day in DEFAULT_SCHEDULE and len(DEFAULT_SCHEDULE[day]) > slot_index:
        del DEFAULT_SCHEDULE[day][slot_index]
        return jsonify({'success': True, 'message': 'Timeslot deleted'})
    else:
        return jsonify({'success': False, 'message': 'Invalid timeslot index'})


@app.route('/add_timeslot', methods=['POST'])
def add_timeslot():
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'User not logged in'})

    day = request.form.get('day')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')

    # Logic to add the new timeslot to the user's default schedule
    user = get_user_by_username(username)
    if user is None:
        return jsonify({'success': False, 'message': 'User not found'})

    if day in DEFAULT_SCHEDULE and len(DEFAULT_SCHEDULE[day]) < 2:
        # Placeholder date used for the TimeSlot constructor
        new_timeslot = TimeSlot('01/01/01', start_time, end_time)
        DEFAULT_SCHEDULE[day].append(new_timeslot)
        return jsonify({'success': True, 'message': 'Timeslot added'})
    else:
        return jsonify({'success': False, 'message': 'Reached maximum timeslots for the day'})


def parse_date(date_str):
    # Expected format: 2024-02-10T05:00:00.000Z
    corrected_date_str = date_str.split('T')[0]  # Extracting only the date part
    return datetime.strptime(corrected_date_str, '%Y-%m-%d')


@app.route('/submit_timesheet', methods=['POST'])
def submit_timesheet():
    username = session.get('username')
    if not username:
        flash('You must be logged in to submit a timesheet.')
        return redirect(url_for('index'))

    pay_period_selection = request.form.get('pay_period')
    start_date = parse_date(pay_period_selection)

    pay_period = PayPeriod(start_date.strftime('%m/%d/%y'))

    for key in request.form:
        if 'slot' in key and ('-start' in key or '-end' in key):
            date_str, slot, time_type = key.split('-')
            date_obj = datetime.strptime(date_str, '%m/%d/%Y').strftime('%m/%d/%y')
            start_time = request.form.get(f'{date_str}-slot1-start')
            end_time = request.form.get(f'{date_str}-slot1-end')
            if 'slot2' in key:
                start_time_2 = request.form.get(f'{date_str}-slot2-start')
                end_time_2 = request.form.get(f'{date_str}-slot2-end')
                if start_time_2 and end_time_2:
                    timeslot_2 = TimeSlot(date_obj, start_time_2, end_time_2)
                    pay_period.add_timeslot(timeslot_2)

            if start_time and end_time:
                timeslot = TimeSlot(date_obj, start_time, end_time)
                pay_period.add_timeslot(timeslot)

    pay_period.remove_duplicate_slots()
    zz = pay_period.serialize()
    print(zz)
    flash('Timesheet submitted successfully.')
    return redirect(url_for('user_home'))


def timeslot_exists(pay_period, new_timeslot):
    for existing_slot in pay_period.get_timesheet_by_date(new_timeslot.get_date()):
        if existing_slot.get_start() == new_timeslot.get_start() and existing_slot.get_end() == new_timeslot.get_end():
            return True
    return False


if __name__ == '__main__':
    app.run(debug=True)
