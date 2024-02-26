import hashlib
from StandardUser import StandardUser
from TimeSlot import TimeSlot
# from datetime import datetime, timedelta
from PayPeriod import PayPeriod
# from datetime import timedelta
import gradio as gr
import datetime
import streamlit as st
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import requests
import os
from dotenv import load_dotenv
import time
from random import getrandbits

load_dotenv()
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')

ADMIN_PIN = os.getenv('ADMIN_PIN')

st.set_page_config(page_title="Timesheet Portal", layout="centered")
# WHY DOES THIS NOT WORK ARGRGGDGHFJKGHKDFGHKLASDfgIOASUDFRghIOASDFG
# st.markdown(
#     # """
#     # <style>
#     # [data-testid="stVerticalBlock"] {
#     #     width: 1000px !important;
#     #     margin: auto !important;
#     #     overflow: hidden !important;
#     # }
#     # [data-testid="stForm"] {
#     #     width: 600px !important;
#     #     }
#     # </style>
#     # """,
#     unsafe_allow_html=True,
# )

if 'DEFAULT_SCHEDULE' not in st.session_state:
    st.session_state.DEFAULT_SCHEDULE = {
        'Sunday': [],
        'Monday': [TimeSlot('01/03/23', '09:00', '11:00'), TimeSlot('01/03/23', '13:00', '17:00')],
        'Tuesday': [TimeSlot('01/04/23', '09:10', '12:00'), TimeSlot('01/04/23', '14:00', '17:00')],
        'Wednesday': [TimeSlot('01/05/23', '09:50', '12:00'), TimeSlot('01/05/23', '15:00', '17:00')],
        'Thursday': [TimeSlot('01/06/23', '09:40', '12:00'), TimeSlot('01/06/23', '16:00', '17:00')],
        'Friday': [TimeSlot('01/07/23', '09:30', '12:00'), TimeSlot('01/07/23', '16:30', '17:00')],
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
    st.write("For auto filling password, click on the password field, not the username field.")
    form = st.form(key='login_form')

    username = form.text_input("Username")
    password = form.text_input("Password", type='password')

    form.checkbox("Remember me")  # doesnt work lol
    # ################ Add remember me functionality #################
    if form.form_submit_button("Sign In"):
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
        col3, col4 = st.columns(2)
        with col3:
            if st.button("See Past Timesheets"):
                st.session_state.page_history.append(st.session_state.current_page)
                st.session_state.current_page = 'past_timesheets'
                st.rerun()
        with col4:
            if st.button("Submit a Timesheet"):
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


def past_timesheets_page():
    st.title("Past Timesheets")
    st.write("This is the past timesheets page.")
    st.write("Here, the user can view their past timesheets and some interesting statistics about their work.")


def all_timesheets_page():
    st.title("Submit a Timesheets")

    # show all the timesheets for the user

    def get_week_range(date):
        known_start_date = datetime.date(2024, 2, 11)
        delta = date - known_start_date
        days_since_last_period_start = delta.days % 14
        start_date = date - datetime.timedelta(days=days_since_last_period_start)
        end_date = start_date + datetime.timedelta(days=13)
        return start_date, end_date

    if 'current_week' not in st.session_state:
        st.session_state.current_week = datetime.date.today()

    week_start, week_end = get_week_range(st.session_state.current_week)

    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        if st.button('<<'):
            st.session_state.current_week -= datetime.timedelta(days=14)
            st.toast("Loading...")
            time.sleep(1)
            # st.toast("Done!", icon='🎉')
            st.rerun()
    with col2:
        st.write(f"Timesheet for week: {week_start.strftime('%A %d %b %Y')} - {week_end.strftime('%A %d %b %Y')}")

    with col3:
        if st.button('\>>'):
            st.session_state.current_week += datetime.timedelta(days=14)
            st.toast("Loading...")
            time.sleep(1)
            # st.toast("Done!", icon='🎉')
            st.rerun()

    st.write("Please enter your timesheet for the week. Enter the times in 24-hour format (HH\:MM). "
             "If you did not work on a particular day, leave the fields empty.")

    st.write("For example, if you worked from 9:00 AM to 5:00 PM, enter 09:00 in From and 17:00 in Till")

    st.write("")

    x, y = st.columns([1, 2])

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    with x:
        st.write("")
        if st.button("Submit Without Any Changes"):
            # cool random animation :)
            # if not not random.getrandbits(1):
            #     st.snow()
            #     time.sleep(4)
            # else:
            #     st.balloons()
            #     time.sleep(3)
            st.toast("Saving the timesheet...")
            time.sleep(1)
            st.toast("Mailing it to Mae and Julia...")
            time.sleep(1)
            st.toast("Done!", icon='🎉')
            # time.sleep(0.5)
            st.success("Timesheet submitted successfully!")
            time.sleep(0.8)
            for day in days:
                print(day, '\n', st.session_state[day][f"1_{day}_from_1"], ' to ',
                      st.session_state[day][f"1_{day}_till_1"],
                      '\n', st.session_state[day][f"1_{day}_from_2"], ' to ', st.session_state[day][f"1_{day}_till_2"])

                print(day, '\n', st.session_state[day][f"2_{day}_from_1"], ' to ',
                      st.session_state[day][f"2_{day}_till_1"],
                      '\n', st.session_state[day][f"2_{day}_from_2"], ' to ', st.session_state[day][f"2_{day}_till_2"])
            st.success("Redirecting to dashboard...")
            time.sleep(1)
            st.session_state.current_page = 'dashboard'
            st.rerun()
    with y:
        st.write("This will submit the timesheet with the default schedule."
                 " If you want to make changes, please do so before submitting."
                 " There's another submit button at the bottom of the page. Scroll down for total hours")

    st.write("")
    st.session_state.total_hours = 0

    for day in days:
        if day not in st.session_state:
            st.session_state[day] = {}

    username = st.session_state.user_info['username']
    user = None
    for i in st.session_state.USERS:
        if i.username == username:
            user = i
            break

    if user is not None:
        schedule = user.default_schedule
    else:
        st.error("User not found. Please contact the administrator (or try logging in again).")
        return

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
            try:
                value = schedule[day][0].get_start().strftime('%H:%M')
            except:
                value = ''
            st.session_state[day][f"1_{day}_from_1"] = st.text_input(f"From", key=f"1_{day}_from_1", value=value)
            if len(st.session_state[day][f"1_{day}_from_1"]) != 5 and st.session_state[day][f"1_{day}_from_1"] != '':
                st.error("Invalid format.")
            elif ':' not in st.session_state[day][f"1_{day}_from_1"] and st.session_state[day][f"1_{day}_from_1"] != '':
                st.error("Invalid format.")
            try:
                start_time_1 = st.session_state[day][f"1_{day}_from_1"]
                start_time_1 = datetime.datetime.strptime(start_time_1, '%H:%M')
            except:
                start_time_1 = None

        with col4:
            try:
                value = schedule[day][0].get_end().strftime('%H:%M')
            except:
                value = ''
            st.session_state[day][f"1_{day}_till_1"] = st.text_input(f"Till", key=f"1_{day}_till_1", value=value)
            if len(st.session_state[day][f"1_{day}_till_1"]) != 5 and st.session_state[day][f"1_{day}_till_1"] != '':
                st.error("Invalid format.")
            elif ':' not in st.session_state[day][f"1_{day}_till_1"] and st.session_state[day][f"1_{day}_till_1"] != '':
                st.error("Invalid format.")
            try:
                end_time_1 = st.session_state[day][f"1_{day}_till_1"]
                end_time_1 = datetime.datetime.strptime(end_time_1, '%H:%M')
            except:
                end_time_1 = None

        with col5:
            try:
                value = schedule[day][1].get_start().strftime('%H:%M')
            except:
                value = ''
            st.session_state[day][f"1_{day}_from_2"] = st.text_input(f"From", key=f"1_{day}_from_2", value=value)
            if len(st.session_state[day][f"1_{day}_from_2"]) != 5 and st.session_state[day][f"1_{day}_from_2"] != '':
                st.error("Invalid format.")
            elif ':' not in st.session_state[day][f"1_{day}_from_2"] and st.session_state[day][f"1_{day}_from_2"] != '':
                st.error("Invalid format.")
            try:
                start_time_2 = st.session_state[day][f"1_{day}_from_2"]
                start_time_2 = datetime.datetime.strptime(start_time_2, '%H:%M')
            except:
                start_time_2 = None

        with col6:
            try:
                value = schedule[day][1].get_end().strftime('%H:%M')
            except:
                value = ''
            st.session_state[day][f"1_{day}_till_2"] = st.text_input(f"Till", key=f"1_{day}_till_2", value=value)
            if len(st.session_state[day][f"1_{day}_till_2"]) != 5 and st.session_state[day][f"1_{day}_till_2"] != '':
                st.error("Invalid format.")
            elif ':' not in st.session_state[day][f"1_{day}_till_2"] and st.session_state[day][f"1_{day}_till_2"] != '':
                st.error("Invalid format.")
            try:
                end_time_2 = st.session_state[day][f"1_{day}_till_2"]
                end_time_2 = datetime.datetime.strptime(end_time_2, '%H:%M')
            except:
                end_time_2 = None

        with col7:
            st.write("")
            st.write("")
            try:
                total_hours = 0
                if start_time_1 is not None and end_time_1 is not None:
                    total_hours = round(((end_time_1 - start_time_1).seconds / 3600), 1)
                if start_time_2 is not None and end_time_2 is not None:
                    total_hours += round(((end_time_2 - start_time_2).seconds / 3600), 1)
                if total_hours == 0:
                    raise ValueError
                st.write(total_hours)
            except:
                st.write("0.00")

    for day in days:
        if st.session_state[day][f"1_{day}_from_1"] != '' and st.session_state[day][f"1_{day}_till_1"] != '':
            if st.session_state[day][f"1_{day}_from_1"] > st.session_state[day][f"1_{day}_till_1"]:
                st.error(f"Invalid times for {day}. Start time must be before end time.")
        if st.session_state[day][f"1_{day}_from_2"] != '' and st.session_state[day][f"1_{day}_till_2"] != '':
            if st.session_state[day][f"1_{day}_from_2"] > st.session_state[day][f"1_{day}_till_2"]:
                st.error(f"Invalid times for {day}. Start time must be before end time.")

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    # i know this is a bad way to do it but i'm too lazy to fix it :/
    for i, day in enumerate(days):
        col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
        with col1:
            st.write("")
            st.write("")
            st.write(day)

        with col2:
            st.write("")
            st.write("")
            date = week_start + datetime.timedelta(days=i + 7)
            st.write(date.strftime('%d %b'))

        with col3:
            try:
                value = schedule[day][0].get_start().strftime('%H:%M')
            except:
                value = ''
            st.session_state[day][f"2_{day}_from_1"] = st.text_input(f"From", key=f"2_{day}_from_1", value=value)
            if len(st.session_state[day][f"2_{day}_from_1"]) != 5 and st.session_state[day][f"2_{day}_from_1"] != '':
                st.error("Invalid format.")
            elif ':' not in st.session_state[day][f"2_{day}_from_1"] and st.session_state[day][f"2_{day}_from_1"] != '':
                st.error("Invalid format.")

            try:
                start_time_1 = st.session_state[day][f"2_{day}_from_1"]
                start_time_1 = datetime.datetime.strptime(start_time_1, '%H:%M')
            except:
                start_time_1 = None

        with col4:
            try:
                value = schedule[day][0].get_end().strftime('%H:%M')
            except:
                value = ''
            st.session_state[day][f"2_{day}_till_1"] = st.text_input(f"Till", key=f"2_{day}_till_1", value=value)
            if len(st.session_state[day][f"2_{day}_till_1"]) != 5 and st.session_state[day][f"2_{day}_till_1"] != '':
                st.error("Invalid format.")
            elif ':' not in st.session_state[day][f"2_{day}_till_1"] and st.session_state[day][f"2_{day}_till_1"] != '':
                st.error("Invalid format.")
            try:
                end_time_1 = st.session_state[day][f"2_{day}_till_1"]
                end_time_1 = datetime.datetime.strptime(end_time_1, '%H:%M')
            except:
                end_time_1 = None

        with col5:
            try:
                value = schedule[day][1].get_start().strftime('%H:%M')
            except:
                value = ''
            st.session_state[day][f"2_{day}_from_2"] = st.text_input(f"From", key=f"2_{day}_from_2", value=value)
            if len(st.session_state[day][f"2_{day}_from_2"]) != 5 and st.session_state[day][f"2_{day}_from_2"] != '':
                st.error("Invalid format.")
            elif ':' not in st.session_state[day][f"2_{day}_from_2"] and st.session_state[day][f"2_{day}_from_2"] != '':
                st.error("Invalid format.")
            try:
                start_time_2 = st.session_state[day][f"2_{day}_from_2"]
                start_time_2 = datetime.datetime.strptime(start_time_2, '%H:%M')
            except:
                start_time_2 = None

        with col6:
            try:
                value = schedule[day][1].get_end().strftime('%H:%M')
            except:
                value = ''
            st.session_state[day][f"2_{day}_till_2"] = st.text_input(f"Till", key=f"2_{day}_till_2", value=value)
            if len(st.session_state[day][f"2_{day}_till_2"]) != 5 and st.session_state[day][f"2_{day}_till_2"] != '':
                st.error("Invalid format.")
            elif ':' not in st.session_state[day][f"2_{day}_till_2"] and st.session_state[day][f"2_{day}_till_2"] != '':
                st.error("Invalid format.")
            try:
                end_time_2 = st.session_state[day][f"2_{day}_till_2"]
                end_time_2 = datetime.datetime.strptime(end_time_2, '%H:%M')
            except:
                end_time_2 = None

        with col7:
            st.write("")
            st.write("")
            try:
                total_hours = 0
                if start_time_1 is not None and end_time_1 is not None:
                    total_hours = round(((end_time_1 - start_time_1).seconds / 3600), 1)
                if start_time_2 is not None and end_time_2 is not None:
                    total_hours += round(((end_time_2 - start_time_2).seconds / 3600), 1)
                if total_hours == 0:
                    raise ValueError
                st.write(total_hours)
            except:
                st.write("0.00")

    # validate the timesheet
    for day in days:
        if st.session_state[day][f"2_{day}_from_1"] != '' and st.session_state[day][f"2_{day}_till_1"] != '':
            if st.session_state[day][f"2_{day}_from_1"] > st.session_state[day][f"2_{day}_till_1"]:
                st.error(f"Invalid times for {day}. Start time must be before end time.")
        if st.session_state[day][f"2_{day}_from_2"] != '' and st.session_state[day][f"2_{day}_till_2"] != '':
            if st.session_state[day][f"2_{day}_from_2"] > st.session_state[day][f"2_{day}_till_2"]:
                st.error(f"Invalid times for {day}. Start time must be before end time.")

    # col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])
    #
    # with col1:
    #     st.write("Total Hours")
    #
    # with col7:
    #     st.write("0.00")

    # when user clicks submit, print the timesheet

    # calculate the total hours

    pay_period = PayPeriod(week_start.strftime('%m/%d/%y'))

    timeslots = []

    for i, day in enumerate(days):
        if st.session_state[day][f"1_{day}_from_1"] != '' and st.session_state[day][f"1_{day}_till_1"] != '':
            timeslots.append(TimeSlot((week_start + datetime.timedelta(days=i)).strftime('%m/%d/%y'),
                                      st.session_state[day][f"1_{day}_from_1"],
                                      st.session_state[day][f"1_{day}_till_1"]))
        if st.session_state[day][f"1_{day}_from_2"] != '' and st.session_state[day][f"1_{day}_till_2"] != '':
            timeslots.append(TimeSlot((week_start + datetime.timedelta(days=i)).strftime('%m/%d/%y'),
                                      st.session_state[day][f"1_{day}_from_2"],
                                      st.session_state[day][f"1_{day}_till_2"]))
        if st.session_state[day][f"2_{day}_from_1"] != '' and st.session_state[day][f"2_{day}_till_1"] != '':
            timeslots.append(TimeSlot((week_start + datetime.timedelta(days=i + 7)).strftime('%m/%d/%y'),
                                      st.session_state[day][f"2_{day}_from_1"],
                                      st.session_state[day][f"2_{day}_till_1"]))
        if st.session_state[day][f"2_{day}_from_2"] != '' and st.session_state[day][f"2_{day}_till_2"] != '':
            timeslots.append(TimeSlot((week_start + datetime.timedelta(days=i + 7)).strftime('%m/%d/%y'),
                                      st.session_state[day][f"2_{day}_from_2"],
                                      st.session_state[day][f"2_{day}_till_2"]))

    for i in timeslots:
        pay_period.add_timeslot(i)

    st.session_state.total_hours = pay_period.get_total_hours()

    st.write(f"Total Hours: ", round(st.session_state.total_hours, 1))

    if st.button("Submit"):

        # Converting the timesheet to a list of TimeSlot objects with pay period

        print(pay_period.get_timesheet_by_pay_period())

        # cool random animation :)
        # if not not random.getrandbits(1):
        #     st.snow()
        #     time.sleep(4)
        # else:
        #     st.balloons()
        #     time.sleep(3)

        st.toast("Saving the timesheet...")
        time.sleep(1)
        st.toast("Mailing it to Mae and Julia...")
        time.sleep(1)
        st.toast("Done!", icon='🎉')
        # time.sleep(0.5)
        st.success("Timesheet submitted successfully!")
        time.sleep(0.8)
        st.success("Redirecting to dashboard...")
        time.sleep(1)
        # st.session_state.current_page = 'dashboard'
        # st.rerun()


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
elif st.session_state.current_page == 'past_timesheets':
    past_timesheets_page()

# Feature to add:
# -> Cookies
# -> Mail the timesheet to the admin when user clicks submit
# -> Send the confirmation email to the user when they submit
# -> Disable the already submitted time sheets
# -> Add some more elements in the StandardUser class to display in the dashboard
# -> Add the ability to edit the default schedule
# -> Add a back button to all pages
# -> Add a dashboard button to all pages
# -> Design the Admin Dashboard
# -> Create Admin Dashboard
# -> OTP for registration
# -> Only msu.edu email addresses allowed
# -> Only Mae and Julia can be admins
