from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import hashlib
from StandardUser import StandardUser
from TimeSlot import TimeSlot
from datetime import datetime, timedelta
from PayPeriod import PayPeriod
from datetime import timedelta

app = Flask(__name__)
app.secret_key = 'richard_simmons'

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


if __name__ == '__main__':
    app.run(debug=True, port=8000)
