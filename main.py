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
import requests
import os
from dotenv import load_dotenv

load_dotenv()
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')

ADMIN_PIN = os.getenv('ADMIN_PIN')

st.set_page_config(page_title="Timesheet Portal")

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
        StandardUser('admin', hashlib.sha256('admin'.encode()).hexdigest(), 'admin', 'MSU', 'admin@msu.edu'
                     , st.session_state.DEFAULT_SCHEDULE),
        StandardUser('Manan', hashlib.sha256('Manan'.encode()).hexdigest(), 'user', 'MSU', 'vyasmana@msu.edu',
                     st.session_state.DEFAULT_SCHEDULE)]

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

# A list to keep track of the page history
if 'page_history' not in st.session_state:
    st.session_state.page_history = []


def login_page():
    # col1, col2, col3 = st.columns(3)

    # with col1:
    #     if st.button("Home"):
    #         st.session_state.current_page = 'login'
    #         st.rerun()
    #
    # with col2:
    #     if st.button("Dashboard"):
    #         if 'user_info' not in st.session_state:
    #             st.error("You must be logged in to access the dashboard.")
    #             time.sleep(1)
    #             st.rerun()
    #         elif st.session_state.user_info['role'] == 'admin':
    #             st.session_state.current_page = 'admin_dashboard'
    #             st.rerun()
    #         else:
    #             st.session_state.current_page = 'dashboard'
    #             st.rerun()
    #
    # with col3:
    #     if st.button("About"):
    #         st.session_state.current_page = 'about'
    #         st.rerun()

    st.title("Sign In")
    st.subheader("Sign in to the Timesheet Portal")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    st.checkbox("Remember me")  # doesnt work lol

    if st.button("Sign In"):
        hashed_pwd = hashlib.sha256(password.encode()).hexdigest()
        # Authenticate user
        user = None
        for i in st.session_state.USERS:
            if i.username == username and i.password == hashed_pwd:
                user = i
                break

        if user:
            st.session_state.user_info = {'username': user.username, 'role': user.role}  # Save user info
            if user.role == 'admin':
                st.session_state.page_history.append(st.session_state.current_page)
                st.session_state.current_page = 'admin_dashboard'
            else:
                st.session_state.page_history.append(st.session_state.current_page)
                st.session_state.current_page = 'dashboard'
            st.rerun()
        else:
            st.error("Invalid Username or Password")

    # st.write("Forgot password?")
    if st.button("Forgot password?"):
        st.session_state.page_history.append(st.session_state.current_page)
        st.session_state.current_page = 'forgot_password'
        st.rerun()

    if st.button("Click here to register"):
        st.session_state.page_history.append(st.session_state.current_page)
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
    st.title("Dashboard")
    user = None
    for i in st.session_state.USERS:
        if i.username == st.session_state.user_info['username']:
            user = i
            break
    if user is None:
        st.error("User not found. Please contact the administrator (or create an account).")
        return

    col1, col2 = st.columns(2)

    with col1:
        st.header(user.username)
        st.image("https://via.placeholder.com/150", width=150)  # Placeholder for user image
        st.write(f"Name: Manan Vyas")
        st.write(f"Email: vyasmana@msu.edu")
        st.write(f"Phone: (517) 980-1536")
        st.write(f"Town: East Lansing")

    with col2:
        st.header("Timesheets")
        if st.button("See All Timesheets"):
            st.session_state.page_history.append(st.session_state.current_page)
            st.session_state.current_page = 'all_timesheets'
            st.rerun()

        timesheet_df = create_timesheet_data()
        timesheet_chart = plot_timesheet_bar_chart(timesheet_df)
        st.pyplot(timesheet_chart)

        st.write("Timesheet Status:")
        st.markdown("""
        - ![#008000](https://via.placeholder.com/15/008000/000000?text=+) `Approved`
        - ![#FF0000](https://via.placeholder.com/15/FF0000/000000?text=+) `Rejected`
        - ![#0000FF](https://via.placeholder.com/15/0000FF/000000?text=+) `Submitted`
        """, unsafe_allow_html=True)


def all_timesheets_page():
    st.title("Submit a Timesheets")

    # show all the timesheets for the user

    def get_week_range(date):
        start = date - datetime.timedelta(days=date.weekday())
        end = start + datetime.timedelta(days=6)
        return start, end

    if 'current_week' not in st.session_state:
        st.session_state.current_week = datetime.date.today()

    week_start, week_end = get_week_range(st.session_state.current_week)

    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        if st.button('<<'):
            st.session_state.current_week -= datetime.timedelta(days=7)
            st.rerun()
    with col2:
        st.write(f"Timesheet for week: {week_start.strftime('%A %d %b %Y')} - {week_end.strftime('%A %d %b %Y')}")

    with col3:
        if st.button('\>>'):
            st.session_state.current_week += datetime.timedelta(days=7)
            st.rerun()

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for day in days:
        if day not in st.session_state:
            st.session_state[day] = {"from": "", "till": ""}

    for i, day in enumerate(days):
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
        with col1:
            st.write("")
            st.write("")
            st.write(day)
        with col2:
            st.write("")
            st.write("")
            date = week_start + datetime.timedelta(days=i)
            st.write(date.strftime('%d %b'))
        with col3:
            st.session_state[day]["from"] = st.text_input(f"From", key=f"{day}_from_1")
        with col4:
            st.session_state[day]["till"] = st.text_input(f"Till", key=f"{day}_till_1")
        with col5:
            st.session_state[day]["from"] = st.text_input(f"From", key=f"{day}_from_2")
        with col6:
            st.session_state[day]["till"] = st.text_input(f"Till", key=f"{day}_till_2")
        with col7:
            st.write("")
            st.write("")
            st.write("0.00")

    if st.button("Submit"):
        pass


def signup_page():
    st.title("Signup Page")
    username = st.text_input("Choose a Username")
    password = st.text_input("Choose a Password", type='password')
    role = st.selectbox("Role", ['user', 'admin'])
    if role == 'admin':
        admin_pin = st.text_input("Admin PIN", type='password')
        if admin_pin != ADMIN_PIN and admin_pin != '':
            st.error("Invalid Admin PIN")
            return
    email = st.text_input("Email Address")
    organization = st.text_input("Organization")

    for i in st.session_state.USERS:
        if i.username == username:
            st.error("Username already exists.")

    if st.button("Create Account"):
        st.session_state.page_history.append(st.session_state.current_page)
        for i in st.session_state.USERS:
            if i.username == username:
                st.error("Username already exists.")
                return
        if password == '':
            st.error("Password cannot be empty.")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long.")
        elif username == '':
            st.error("Username cannot be empty.")
        elif len(username) < 3:
            st.error("Username must be at least 3 characters long.")
        else:
            st.session_state.USERS.append(
                StandardUser(username, password, role, organization, email, st.session_state.DEFAULT_SCHEDULE))
            st.success("Account Created Successfully!")
            time.sleep(1.5)
            st.success("Redirecting to login page...")
            time.sleep(1)
            st.session_state.page_history.append(st.session_state.current_page)
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

        # check if username exists or not
        user = None
        if username != "":
            user = None
            for i in st.session_state.USERS:
                if i.username == username:
                    user = i
                    break

            if user is None:
                st.error("User not found. Please enter a valid username.")

        if email != "" and user is not None:
            if email != user.email_address:
                st.error("Email address does not match the username.")
                # return

        if st.button("Send OTP") and user is not None and email == user.email_address:
            st.session_state.otp = random.randint(1000, 9999)
            print(st.session_state.otp)
            st.session_state.otp_sent = True
            send_otp(username, st.session_state.otp, email)
            st.write(f"An OTP has been sent to your email address: {st.session_state.otp}")
            time.sleep(1)
            st.rerun()

    if st.session_state.otp_sent:
        st.title("Forgot Password")
        st.write("OTP has been sent to your email address (make sure to check spam folder). "
                 "Please enter the OTP to reset your password.")
        username = st.text_input("Username")
        otp = st.text_input("Enter OTP")
        new_password = st.text_input("Enter new password", type='password')
        confirm_password = st.text_input("Confirm new password", type='password')

        if new_password != confirm_password and confirm_password != "":
            st.error("Passwords do not match")

        if st.button("Submit"):
            if otp == str(st.session_state.otp):
                if new_password == confirm_password:
                    user_index = None
                    for i in st.session_state.USERS:
                        if i.username == username:
                            user_index = st.session_state.USERS.index(i)
                            break
                    if user_index is not None:
                        st.session_state.USERS[user_index].set_password(new_password)
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


def send_otp(user, otp, mail):
    senders_name = 'Manan Vyas'
    senders_email = 'timesheet@mananvyas.in'
    receivers_email = mail
    subject = 'One Time Password (OTP) for Password Reset'
    content = (f'Hi {user}, \n\n'
               f'A request to reset your password has been made. Your verification code is: {otp}\n\n\n'
               f'If you did not request this, please ignore this email.\n\n\n'
               f'Thanks,\n'
               f'Your Friendly Neighborhood Spider-man')

    requests.post(
        "https://api.mailgun.net/v3/mananvyas.in/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": f"{senders_name} <{senders_email}>",
              "to": [f"{receivers_email}"],
              "subject": f"{subject}",
              "text": f"{content}"})


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
elif st.session_state.current_page == 'all_timesheets':
    all_timesheets_page()

print(st.session_state.page_history)
