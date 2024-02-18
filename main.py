import hashlib
from StandardUser import StandardUser
from TimeSlot import TimeSlot
# from datetime import datetime, timedelta
from PayPeriod import PayPeriod
# from datetime import timedelta
import gradio as gr
import datetime
import time
import streamlit as st
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


if 'DEFAULT_SCHEDULE' not in st.session_state:
    st.session_state.DEFAULT_SCHEDULE = {
        'Sunday': [],
        'Monday': [TimeSlot('01/03/23', '09:00', '12:00'), TimeSlot('01/03/23', '13:00', '17:00')],
        'Tuesday': [TimeSlot('01/04/23', '09:00', '12:00'), TimeSlot('01/04/23', '13:00', '17:00')],
        'Wednesday': [TimeSlot('01/05/23', '09:00', '12:00'), TimeSlot('01/05/23', '13:00', '17:00')],
        'Thursday': [TimeSlot('01/06/23', '09:00', '12:00'), TimeSlot('01/06/23', '13:00', '17:00')],
        'Friday': [TimeSlot('01/07/23', '09:00', '12:00'), TimeSlot('01/07/23', '13:00', '17:00')],
        'Saturday': []
    }

if 'USERS' not in st.session_state:
    st.session_state.USERS = [
        ['user1', hashlib.sha256('password1'.encode()).hexdigest(), 'admin', 'org1', []],
        ['user2', hashlib.sha256('password2'.encode()).hexdigest(), 'user', 'org2', []],
        ['Manan', hashlib.sha256('Manan'.encode()).hexdigest(), 'user', 'org3', []]
    ]

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'


def login_page():
    st.title("Sign In")
    st.subheader("Sign in to the Timesheet Portal")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    st.checkbox("Remember me")  # doesnt work lol

    if st.button("Sign In"):
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        # Authenticate user
        user = next((user for user in st.session_state.USERS if user[0] == username and user[1] == hashed_pwd), None)
        if user:
            st.session_state.user_info = {'username': user[0], 'role': user[2]}  # Save user info
            if user[2] == 'admin':
                st.session_state.current_page = 'admin_dashboard'
            else:
                st.session_state.current_page = 'dashboard'
            st.rerun()
        else:
            st.error("Invalid Username or Password")

    # st.write("Forgot password?")
    if st.button("Forgot password?"):
        st.session_state.current_page = 'forgot_password'
        st.rerun()

    if st.button("Click here to register"):
        st.session_state.current_page = 'signup'
        st.rerun()


def admin_dashboard_page():
    st.title("Admin Dashboard")
    st.write(f"Welcome, {st.session_state.user_info['username']} (Admin)")
    st.write("This is the admin dashboard.")


def create_timesheet_data():
    # create some dummy data
    today = datetime.date.today()
    last_four_sundays = [(today - pd.Timedelta(days=(today.weekday() + 1) % 7 + 7 * i)) for i in range(5)]
    last_four_sundays = last_four_sundays[::-1]
    data = {
        'Date': [date.strftime('%d %b') for date in last_four_sundays],
        'Hours': [10, 20, 30, 40, 20],
        'Status': ['Approved', 'Rejected', 'Submitted', 'Approved', 'Submitted']
    }
    df = pd.DataFrame(data)
    return df


def plot_timesheet_bar_chart(df):

    plt.style.use('dark_background')
    status_colors = {'Approved': 'green', 'Rejected': 'red', 'Submitted': 'blue'}
    colors = df['Status'].map(status_colors)
    fig, ax = plt.subplots()
    bars = ax.bar(df['Date'], df['Hours'], color=colors, width=0.2)

    ax.set_facecolor('#0f1116')
    fig.patch.set_facecolor('#0f1116')
    ax.set_xlabel('Date', fontsize=12, color='white')
    ax.set_ylabel('Hours', fontsize=12, color='white')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.set_ylim(0, 40)
    ax.set_title('Timesheets', fontsize=14, color='white')

    ax.xaxis.labelpad = 15
    ax.yaxis.labelpad = 15

    return fig


def dashboard_page():
    user = next((user for user in st.session_state.USERS if user[0] == st.session_state.user_info['username']), None)
    if user:
        user = StandardUser(user[0], user[1], user[2], user[3], st.session_state.DEFAULT_SCHEDULE, user[4])
    else:
        st.error("User not found. Please contact the administrator (or create an account).")

    col1, col2 = st.columns(2)

    with col1:
        st.header(user.username)
        st.image("https://via.placeholder.com/150", width=150)  # Placeholder for user image
        st.write(f"Name: Manan Vyas")
        st.write(f"Email: vyasmana@msu.edu")
        st.write(f"Phone: (517) 980-1536")
        st.write(f"Town: Yo Momma")

    with col2:
        st.header("Timesheets")
        st.button("See All Timesheets")
        timesheet_df = create_timesheet_data()
        timesheet_chart = plot_timesheet_bar_chart(timesheet_df)
        st.pyplot(timesheet_chart)

        st.write("Timesheet Status:")
        st.markdown("""
        - ![#008000](https://via.placeholder.com/15/008000/000000?text=+) `Approved`
        - ![#FF0000](https://via.placeholder.com/15/FF0000/000000?text=+) `Rejected`
        - ![#0000FF](https://via.placeholder.com/15/0000FF/000000?text=+) `Submitted`
        """, unsafe_allow_html=True)


def signup_page():
    st.title("Signup Page")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type='password')
    role = st.selectbox("Role", ['admin', 'user'])
    organization = st.text_input("Organization")
    hashed_pwd = hashlib.sha256(password.encode()).hexdigest()

    if st.button("Create Account"):
        st.session_state.USERS.append([username, hashed_pwd, role, organization])
        st.success("Account Created Successfully!")
        st.session_state.current_page = 'login'
        st.rerun()


def forgot_password_page():
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False
    if 'otp' not in st.session_state:
        st.session_state.otp = None

    if not st.session_state.otp_sent:
        st.title("Forgot Password")
        st.write("Please enter your email address to receive a password reset link.")
        username = st.text_input("Username")
        password = st.text_input("Enter the last password you remember", type='password')
        email = st.text_input("Email address")

        if st.button("Send OTP"):
            st.session_state.otp = random.randint(1000, 9999)
            print(st.session_state.otp)
            st.session_state.otp_sent = True
            st.write(f"An OTP has been sent to your email address: {st.session_state.otp}")  # For testing only
            st.rerun()

    if st.session_state.otp_sent:
        st.title("Forgot Password")
        st.write("OTP has been sent to your email address (make sure to check spam folder). "
                 "Please enter the OTP to reset your password.")
        username = st.text_input("Username")
        otp = st.text_input("Enter OTP")
        new_password = st.text_input("Enter new password", type='password')
        confirm_password = st.text_input("Confirm new password", type='password')

        if new_password != confirm_password:
            st.error("Passwords do not match")

        if st.button("Submit"):
            if otp == str(st.session_state.otp):
                if new_password == confirm_password:
                    hashed_pwd = hashlib.sha256(new_password.encode()).hexdigest()
                    user_index = next(
                        (index for index, user in enumerate(st.session_state.USERS) if user[0] == username), None)
                    if user_index is not None:
                        st.session_state.USERS[user_index][1] = hashed_pwd
                        st.success("Password reset successfully!")
                        st.session_state.current_page = 'login'
                        st.session_state.otp_sent = False
                        st.session_state.otp = None
                        time.sleep(1)
                        st.success("Redirecting to login page...")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("User not found.")
                else:
                    st.error("Passwords do not match")
            else:
                st.error("Invalid OTP")


if st.session_state.current_page == 'login':
    login_page()
elif st.session_state.current_page == 'signup':
    signup_page()
elif st.session_state.current_page == 'dashboard':
    dashboard_page()
elif st.session_state.current_page == 'admin_dashboard':
    admin_dashboard_page()
elif st.session_state.current_page == 'forgot_password':
    forgot_password_page()
