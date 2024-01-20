from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import hashlib
from StandardUser import StandardUser
from TimeSlot import TimeSlot

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


@app.route('/submit_timesheet', methods=['POST'])
def submit_timesheet():
    # Handle timesheet submission here
    return redirect(url_for('user_home'))


# Run the Flask app

if __name__ == '__main__':
    app.run(debug=True)
