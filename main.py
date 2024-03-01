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

MAE_NETID = os.getenv('MAE_NETID')
JULIA_NETID = os.getenv('JULIA_NETID')


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
        StandardUser('plattem', hashlib.sha256('admin'.encode()).hexdigest(), 'admin', 'MSU', 'admin@msu.edu'
                     , st.session_state.DEFAULT_SCHEDULE),
        StandardUser('vyasmana', hashlib.sha256('Manan'.encode()).hexdigest(), 'user', 'MSU', 'vyasmana@msu.edu',
                     st.session_state.DEFAULT_SCHEDULE)]

# adding some timesheets to data (to test the dashboard)
user_manan = st.session_state.USERS[1]

second_pay_period = PayPeriod('01/15/23')
custom_timeslots = [
    TimeSlot('01/16/23', '10:00', '15:00'),
    TimeSlot('01/17/23', '10:00', '15:00'),
    TimeSlot('01/18/23', '10:00', '15:00'),
]
user_manan.submit_timesheet(second_pay_period, custom_timeslots)
#
#
pay_period = PayPeriod('02/11/24')
user_manan.submit_default_schedule(pay_period)
pay_period.is_approved = 'approved'


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
            if i._username == username and i._password == hashed_pwd:
                user = i
                break

        if user:
            st.session_state.user_info = {'username': user._username, 'role': user._role}  # Save user info
            if user._role == 'admin':
                st.session_state.page_history.append(st.session_state.current_page)
                st.session_state.current_page = 'dashboard'
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
    current_time = datetime.datetime.now().strftime("%H:%M:%S")

    if "00:00:00" < current_time < "12:00:00":
        st.title(f"Good Morning, {st.session_state.user_info['username']}")
    elif "12:00:00" < current_time < "17:00:00":
        st.title(f"Good Afternoon, {st.session_state.user_info['username']}")
    else:
        st.title(f"Good Evening, {st.session_state.user_info['username']}")

    st.write("Select a user to view their timesheets")

    col1, col2, col3, col4 = st.columns(4)

    dummy_list = [f'dummy_{i}' for i in range(1, 13)]
    user_list = [i._username for i in st.session_state.USERS]

    for i in range(0, 12):
        try:
            dummy_list[i] = user_list[i]
        except:
            continue

    with col1:
        if st.button(dummy_list[0]):
            st.session_state.admin_selected_user = dummy_list[0]
            st.rerun()
        if st.button(dummy_list[4]):
            st.session_state.admin_selected_user = dummy_list[4]
            st.rerun()
        if st.button(dummy_list[8]):
            st.session_state.admin_selected_user = dummy_list[8]
            st.rerun()
    with col2:
        if st.button(dummy_list[1]):
            st.session_state.admin_selected_user = dummy_list[1]
            st.rerun()
        if st.button(dummy_list[5]):
            st.session_state.admin_selected_user = dummy_list[5]
            st.rerun()
        if st.button(dummy_list[9]):
            st.session_state.admin_selected_user = dummy_list[9]
            st.rerun()

    with col3:
        if st.button(dummy_list[2]):
            st.session_state.admin_selected_user = dummy_list[2]
            st.rerun()
        if st.button(dummy_list[6]):
            st.session_state.admin_selected_user = dummy_list[6]
            st.rerun()
        if st.button(dummy_list[10]):
            st.session_state.admin_selected_user = dummy_list[10]
            st.rerun()

    with col4:
        if st.button(dummy_list[3]):
            st.session_state.admin_selected_user = dummy_list[3]
            st.rerun()
        if st.button(dummy_list[7]):
            st.session_state.admin_selected_user = dummy_list[7]
            st.rerun()
        if st.button(dummy_list[11]):
            st.session_state.admin_selected_user = dummy_list[11]
            st.rerun()

    admin_selected_user = None

    try:
        for i in st.session_state.USERS:
            if i._username == st.session_state.admin_selected_user:
                admin_selected_user = i
                break
    except:
        pass

    st.write(" ")

    st.write(f"The users who require your attention are colored in blue. (TODO).")

    st.write("--" * 15)

    if admin_selected_user is not None:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"<p class='big-font'> Past time sheets Graph", unsafe_allow_html=True)

        with col2:
            st.markdown(f"<p class='big-font'>{admin_selected_user._username}\'s Notifications</p>",
                        unsafe_allow_html=True)
            st.markdown("""
            <style>
            .big-font {
                font-size:25px !important;
            }
            </style>
            """, unsafe_allow_html=True)

            col3, col4 = st.columns(2)
            with col3:
                st.write("Actions")
                st.write("Approve/Reject Timesheets")
            with col4:
                st.write("Notifications")


def create_timesheet_data(username='vyasmana'):
    if 'current_week' not in st.session_state:
        st.session_state.current_week = datetime.date.today()
    user = None
    for i in st.session_state.USERS:
        if i._username == username:
            user = i
            break

    if user is None:
        st.error("User not found. Please contact the administrator (or create an account).")
        return

    time_sheets = user._timesheets

    last_five_timeshetes = []
    for i in range(6):
        if i == 5:
            break
        try:
            last_five_timeshetes.append(time_sheets[i]['pay_period'])
        except:
            last_five_timeshetes.append("")

    last_five_pay_periods = []
    for i in range(6):
        if i == 5:
            break
        try:
            last_five_pay_periods.append(last_five_timeshetes[i].get_start_date().strftime('%d %b'))
        except:
            last_five_pay_periods.append("")


    hours = []
    for i in range(6):
        if i == 5:
            break
        try:
            hours.append(last_five_timeshetes[i].get_total_hours())
        except:
            hours.append(0)

    status = []
    for i in range(6):
        if i == 5:
            break
        try:
            status.append(last_five_timeshetes[i].is_approved)
        except:
            status.append('pending')

    data = {
        'Date': last_five_pay_periods,
        'Hours': hours,
        'Status': status
    }

    print(data)

    df = pd.DataFrame(data)
    return df


def plot_timesheet_bar_chart(df):
    plt.style.use('dark_background')
    status_colors = {'approved': 'green', 'rejected': 'red', 'pending': 'blue'}
    colors = df['Status'].map(status_colors)
    fig, ax = plt.subplots()
    bars = ax.bar(df['Date'], df['Hours'], color=colors, width=0.1)

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
        if i._username == st.session_state.user_info['username']:
            user = i
            break
    if user is None:
        st.error("User not found. Please contact the administrator (or create an account).")
        return

    if user._role == 'admin':
        st.session_state.current_page = 'admin_dashboard'
        st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f'{user._username}')
        image_url = "https://via.placeholder.com/150"
        if user._photo:
            image_url = user._photo
        try:
            st.image(image_url, width=150)
        except:
            st.image("https://via.placeholder.com/150", width=150)

        if user._fname is None and user._lname is None:
            st.write("Click on edit profile to add your name.")
        else:
            st.write(f"Name: {user._fname if user._fname else ''} {user._lname if user._lname else ''}")
        st.write(f"Email: {user._email_address}")
        st.write(f"Phone: {user._phone_number if user._phone_number else ''}")
        st.write(f"{user._miscellaneous if user._miscellaneous else ''}")
        if st.button("Edit your profile"):
            st.session_state.current_page = 'edit_profile'
            st.rerun()
        if st.button("Edit default schedule"):
            st.session_state.current_page = 'edit_default_schedule'
            st.rerun()

    with col2:
        st.subheader("Timesheets")
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
        st.write("Here's a graph of your last 5 time sheets")
        timesheet_df = create_timesheet_data()
        timesheet_chart = plot_timesheet_bar_chart(timesheet_df)
        st.pyplot(timesheet_chart)

        st.write("Timesheet Status:")
        st.markdown("""
        - ![#008000](https://via.placeholder.com/15/008000/000000?text=+) `Approved`
        - ![#FF0000](https://via.placeholder.com/15/FF0000/000000?text=+) `Rejected (Highly Unlikely)`
        - ![#0000FF](https://via.placeholder.com/15/0000FF/000000?text=+) `Submitted`
        """, unsafe_allow_html=True)


def past_timesheets_page():
    st.title("Past Timesheets")
    st.write("This is the past timesheets page.")
    st.write("Here, the user can view their past timesheets and some interesting statistics about their work.")
    if st.button("Back to Dashboard"):
        st.session_state.current_page = 'dashboard'
        st.rerun()


# https://discuss.streamlit.io/t/hide-fullscreen-option-when-displaying-images-using-st-image/19792
# no more full screen :)
hide_img_fs = '''
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
'''

st.markdown(hide_img_fs, unsafe_allow_html=True)


def get_week_range(date):
    known_start_date = datetime.date(2024, 2, 11)
    delta = date - known_start_date
    days_since_last_period_start = delta.days % 14
    start_date = date - datetime.timedelta(days=days_since_last_period_start)
    end_date = start_date + datetime.timedelta(days=13)
    return start_date, end_date


def all_timesheets_page():
    st.title("Submit a Timesheets")

    if st.button("Back to Dashboard"):
        st.session_state.current_page = 'dashboard'
        st.rerun()

    # show all the timesheets for the user

    if 'current_week' not in st.session_state:
        st.session_state.current_week = datetime.date.today()

    week_start, week_end = get_week_range(st.session_state.current_week)

    col1, col2, col3 = st.columns([1, 6, 1])
    with col1:
        if st.button('<<'):
            st.session_state.current_week -= datetime.timedelta(days=14)
            st.toast("Loading...")
            time.sleep(1)
            # st.toast("Done!", icon='🎉')
            st.rerun()
    with col2:
        st.subheader(f"{week_start.strftime('%A %d %b %Y')} - {week_end.strftime('%A %d %b %Y')}")

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
        if i._username == username:
            user = i
            break

    if user is not None:
        schedule = user._default_schedule
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

    # print(pretty_print_timesheet(pay_period))

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


def pretty_print_timesheet(pay_period):
    output = [f"Pay Period Start Date: {pay_period.get_start_date().strftime('%m/%d/%y')}",
              f"Pay Period End Date: {pay_period.get_end_date().strftime('%m/%d/%y')}\n"]

    timesheet = pay_period.get_timesheet_by_pay_period()

    sorted_dates = sorted(timesheet.keys(), key=lambda x: datetime.datetime.strptime(x, '%m/%d/%y'))

    for date_str in sorted_dates:
        timeslots = timesheet[date_str]
        output.append(f"Date: {date_str}")
        for slot in timeslots:
            start_time = slot.get_start().strftime('%H:%M')
            end_time = slot.get_end().strftime('%H:%M')
            output.append(f" - Time Slot: {start_time} to {end_time}")

    return "\n".join(output)


def signup_page():
    st.title("Signup Page")
    st.write("Want to go back to the login page? Click the button below.")
    if st.button("Login"):
        st.session_state.current_page = 'login'
        st.rerun()
    username = st.text_input("Enter your username (should be your NetID)")
    password = st.text_input("Choose a Password", type='password')
    if 8 > len(password) > 0:
        st.error("Password must be at least 8 characters long.")
    role = st.selectbox("Role", ['user', 'admin'])
    if role == 'admin' and username != '':
        if not (username == MAE_NETID or username == JULIA_NETID):
            st.error("Only Mae and Julia can sign up as an admin.")
            return
        admin_pin = st.text_input("Admin PIN", type='password')
        if admin_pin != ADMIN_PIN and admin_pin != '':
            st.error("Invalid Admin PIN, please refer to your email for the admin PIN.")
            return

    organization = st.text_input("Organization")

    if 'create_account_otp' not in st.session_state:
        st.session_state.create_account_otp = None

    for i in st.session_state.USERS:
        if i._username == username:
            st.error("Username already exists.")
    if st.session_state.create_account_otp is None:
        if st.button("Send OTP"):
            st.session_state.create_account_otp = random.randint(1000, 9999)
            print(st.session_state.create_account_otp)
            send_otp(username, st.session_state.create_account_otp, username + '@msu.edu', create_account=True)
            st.success(f"An OTP has been sent to your email address: {st.session_state.create_account_otp}")
            time.sleep(1)
            st.rerun()
    else:
        otp = st.text_input("Enter OTP")
        if st.button("Create Account"):
            st.session_state.page_history.append(st.session_state.current_page)
            for i in st.session_state.USERS:
                if i._username == username:
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
            elif otp != str(st.session_state.create_account_otp):
                st.error("Invalid OTP")
            else:
                st.session_state.USERS.append(
                    StandardUser(username, password, role, organization, 'email', st.session_state.DEFAULT_SCHEDULE))
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
                if i._username == username:
                    user = i
                    break

            if user is None:
                st.error("User not found. Please enter a valid username.")

        if email != "" and user is not None:
            if email != user._email_address:
                st.error("Email address does not match the username.")
                # return

        if st.button("Send OTP") and user is not None and email == user._email_address:
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
                        if i._username == username:
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


def send_otp(user, otp, mail, create_account=False):
    senders_name = 'Manan Vyas'
    senders_email = 'timesheet@mananvyas.in'
    receivers_email = mail
    if create_account:
        content = (f'Hi {user}, \n\n'
                   f'Your verification code is: {otp}\n\n\n'
                   f'If you did not request this, please ignore this email.\n\n\n')
        if mail == JULIA_NETID + '@msu.edu':
            content += (f'Please note that you are signing up as an admin. \n'
                        f'You will need the admin PIN to complete the sign up process.\n '
                        f'The admin pin is: {ADMIN_PIN}\n\n\n')
        if mail == MAE_NETID + '@msu.edu':
            content += (f'Please note that you are signing up as an admin. \n'
                        f'You will need the admin PIN to complete the sign up process.\n '
                        f'The admin pin is: {ADMIN_PIN}\n\n\n')

        content += (f'Thanks,\n'
                    f'Manan')
        subject = 'One Time Password (OTP) for Account Creation'

    else:
        subject = 'One Time Password (OTP) for Password Reset'
        content = (f'Hi {user}, \n\n'
                   f'A request to reset your password has been made. Your verification code is: {otp}\n\n\n'
                   f'If you did not request this, please ignore this email.\n\n\n'
                   f'Thanks,\n'
                   f'Manan')

    requests.post(
        "https://api.mailgun.net/v3/mananvyas.in/messages",
        auth=("api", MAILGUN_API_KEY),
        data={"from": f"{senders_name} <{senders_email}>",
              "to": [f"{receivers_email}"],
              "subject": f"{subject}",
              "text": f"{content}"})


def edit_default_schedule_page():
    # get the user and display their default schedule
    user = None
    for i in st.session_state.USERS:
        if i._username == st.session_state.user_info['username']:
            user = i
            break
    if user is None:
        st.error("User not found. Please contact the administrator (or create an account).")
        return

    st.title("Edit Default Schedule")
    st.subheader("This is your default schedule. You can edit it here.")
    st.write("Your timesheets will be pre-filled with this schedule. You can edit the timesheets later if you want.")
    st.write("Please enter the times in 24-hour format (HH\:MM). \n"
             "For example, if you work from 9:00 AM to 5:00 PM, enter 09:00 in From and 17:00 in Till")

    st.write("Changed your mind? Don't want to edit it anymore?")
    if st.button("Back to Dashboard"):
        st.session_state.current_page = 'dashboard'
        st.rerun()

    default_schedule = user._default_schedule

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

    # print(default_schedule)

    if 'user_default_schedule' not in st.session_state:
        st.session_state.user_default_schedule = {}

    # for j in days:
    #     if j not in st.session_state['user_default_schedule']:
    #         st.session_state['user_default_schedule'][j] = []

    base_date = datetime.datetime(2023, 1, 2)
    count = 0

    for i in days:
        col1, col2, col3, col4, col5, col6 = st.columns(6)

        with col1:
            st.write("")
            st.write("")
            st.write(i)

        with col2:
            try:
                value = default_schedule[i][0].get_start().strftime('%H:%M')
            except:
                value = ''
            st.session_state['user_default_schedule'][f"{i}_from_1"] = st.text_input(f"From", key=f"{i}_from_1",
                                                                                     value=value)

        with col3:
            try:
                value = default_schedule[i][0].get_end().strftime('%H:%M')
            except:
                value = ''
            st.session_state['user_default_schedule'][f"{i}_till_1"] = st.text_input(f"Till", key=f"{i}_till_1",
                                                                                     value=value)

        with col4:
            try:
                value = default_schedule[i][1].get_start().strftime('%H:%M')
            except:
                value = ''
            st.session_state['user_default_schedule'][f"{i}_from_2"] = st.text_input(f"From", key=f"{i}_from_2",
                                                                                     value=value)

        with col5:
            try:
                value = default_schedule[i][1].get_end().strftime('%H:%M')
            except:
                value = ''
            st.session_state['user_default_schedule'][f"{i}_till_2"] = st.text_input(f"Till", key=f"{i}_till_2",
                                                                                     value=value)

        # print(st.session_state['user_default_schedule'])

        with col6:
            st.write("")
            st.write("")
            try:
                total_hours = 0
                # get total hours from the values entered (session state)
                if st.session_state['user_default_schedule'][f"{i}_from_1"] != '' and \
                        st.session_state['user_default_schedule'][
                            f"{i}_till_1"] != '':
                    start_time_1 = st.session_state['user_default_schedule'][f"{i}_from_1"]
                    start_time_1 = datetime.datetime.strptime(start_time_1, '%H:%M')
                    end_time_1 = st.session_state['user_default_schedule'][f"{i}_till_1"]
                    end_time_1 = datetime.datetime.strptime(end_time_1, '%H:%M')
                    total_hours = round(((end_time_1 - start_time_1).seconds / 3600), 1)

                if st.session_state['user_default_schedule'][f"{i}_from_2"] != '' and \
                        st.session_state['user_default_schedule'][
                            f"{i}_till_2"] != '':
                    start_time_2 = st.session_state['user_default_schedule'][f"{i}_from_2"]
                    start_time_2 = datetime.datetime.strptime(start_time_2, '%H:%M')
                    end_time_2 = st.session_state['user_default_schedule'][f"{i}_till_2"]
                    end_time_2 = datetime.datetime.strptime(end_time_2, '%H:%M')
                    total_hours += round(((end_time_2 - start_time_2).seconds / 3600), 1)
                if total_hours == 0:
                    st.write("0.00")
                else:
                    st.write(total_hours)
            except:
                st.write("0.00")

    total_hours = 0

    for i in days:
        # get total hours from the values entered (session state)
        if st.session_state['user_default_schedule'][f"{i}_from_1"] != '' and \
                st.session_state['user_default_schedule'][
                    f"{i}_till_1"] != '':
            start_time_1 = st.session_state['user_default_schedule'][f"{i}_from_1"]
            start_time_1 = datetime.datetime.strptime(start_time_1, '%H:%M')
            end_time_1 = st.session_state['user_default_schedule'][f"{i}_till_1"]
            end_time_1 = datetime.datetime.strptime(end_time_1, '%H:%M')
            total_hours += round(((end_time_1 - start_time_1).seconds / 3600), 1)

        if st.session_state['user_default_schedule'][f"{i}_from_2"] != '' and \
                st.session_state['user_default_schedule'][
                    f"{i}_till_2"] != '':
            start_time_2 = st.session_state['user_default_schedule'][f"{i}_from_2"]
            start_time_2 = datetime.datetime.strptime(start_time_2, '%H:%M')
            end_time_2 = st.session_state['user_default_schedule'][f"{i}_till_2"]
            end_time_2 = datetime.datetime.strptime(end_time_2, '%H:%M')
            total_hours += round(((end_time_2 - start_time_2).seconds / 3600), 1)

    st.write(f"Total Hours: ", round(total_hours, 1))

    # validate the timesheet
    for day in days:
        if st.session_state['user_default_schedule'][f"{day}_from_1"] != '' and \
                st.session_state['user_default_schedule'][f"{day}_till_1"] != '':
            if st.session_state['user_default_schedule'][f"{day}_from_1"] > st.session_state['user_default_schedule'][
                f"{day}_till_1"]:
                st.error(f"Invalid times for {day}. Start time must be before end time.")
        if st.session_state['user_default_schedule'][f"{day}_from_2"] != '' and \
                st.session_state['user_default_schedule'][f"{day}_till_2"] != '':
            if st.session_state['user_default_schedule'][f"{day}_from_2"] > st.session_state['user_default_schedule'][
                f"{day}_till_2"]:
                st.error(f"Invalid times for {day}. Start time must be before end time.")

        # check for invalid format
        if len(st.session_state['user_default_schedule'][f"{day}_from_1"]) != 5 and \
                st.session_state['user_default_schedule'][f"{day}_from_1"] != '':
            st.error("Invalid format.")
        elif ':' not in st.session_state['user_default_schedule'][f"{day}_from_1"] and \
                st.session_state['user_default_schedule'][f"{day}_from_1"] != '':
            st.error("Invalid format.")

        # check for overlapping times
        if st.session_state['user_default_schedule'][f"{day}_from_1"] != '' and \
                st.session_state['user_default_schedule'][f"{day}_till_1"] != '' and \
                st.session_state['user_default_schedule'][f"{day}_from_2"] != '' and \
                st.session_state['user_default_schedule'][f"{day}_till_2"] != '':
            if st.session_state['user_default_schedule'][f"{day}_from_1"] < st.session_state['user_default_schedule'][
                f"{day}_till_1"] and st.session_state['user_default_schedule'][f"{day}_from_2"] < \
                    st.session_state['user_default_schedule'][f"{day}_till_2"]:
                if st.session_state['user_default_schedule'][f"{day}_till_1"] > \
                        st.session_state['user_default_schedule'][f"{day}_from_2"]:
                    st.error(f"Overlapping times for {day}.")

    if st.button("Save Changes"):
        # God-bless co-pilot
        custom_schedule = {}
        for day in days:
            custom_schedule[day] = []

            day_date_str = (base_date + datetime.timedelta(days=count)).strftime('%m/%d/%y')
            count += 1

            for slot_index in [1, 2]:
                from_key = f"{day}_from_{slot_index}"
                till_key = f"{day}_till_{slot_index}"
                start_time = st.session_state['user_default_schedule'].get(from_key, '').strip()
                end_time = st.session_state['user_default_schedule'].get(till_key, '').strip()

                if start_time and end_time:
                    try:
                        time_slot = TimeSlot(day_date_str, start_time, end_time)
                        if day not in custom_schedule:
                            custom_schedule[day] = []
                        custom_schedule[day].append(time_slot)
                    except ValueError as e:
                        st.error(f"Error creating time slot for {day}: {e}")
                else:
                    if start_time or end_time:
                        st.error(f"Please enter both start and end times for {day} slot {slot_index}")
                        return

        user._default_schedule = custom_schedule

        st.toast("Saving the default schedule...")
        time.sleep(1)
        st.toast("Done!", icon='🎉')
        time.sleep(0.5)
        st.success("Redirecting to dashboard...")
        time.sleep(0.5)
        st.session_state.current_page = 'dashboard'
        st.rerun()


def edit_profile_page():
    st.title("Edit Profile")
    st.subheader("You can edit your profile here.")
    st.write("Changed your mind? Don't want to edit it anymore?")
    if st.button("Go Back to Dashboard"):
        st.session_state.current_page = 'dashboard'
        st.rerun()

    # Edit first name
    # Edit last name
    # Edit photo link
    # Edit Phone Number
    # Misc. Info (Quote, Bio, etc.)

    col1, col2 = st.columns(2)
    user = None

    for i in st.session_state.USERS:
        if i._username == st.session_state.user_info['username']:
            user = i
            break
    if user is None:
        st.error("User not found. Please contact the administrator (or create an account).")
        return

    with col1:
        fname = st.text_input("First Name", value=user._fname)
        phone = st.text_input("Phone Number (Optional)", value=user._phone_number)
        photo_link = st.text_input("Photo URL", value=user._photo,
                                   help="Go to ASN website -> About -> People -> Right click on your photo -> "
                                        "Copy Image Address -> Paste here. (Or upload to imgur and paste the"
                                        " link here)")
    with col2:
        lname = st.text_input("Last Name", value=user._lname)
        misc_info = st.text_area("Miscellaneous Information", value=user._miscellaneous, height=122, help="It can be a quote, a short bio, etc.")

    if st.button("Save Changes"):
        if fname != '':
            user._fname = fname
        if lname != '':
            user._lname = lname
        if phone != '':
            user._phone_number = phone
        if photo_link != '':
            user._photo = photo_link
        if misc_info != '':
            user._miscellaneous = misc_info
        st.toast("Saving your profile...")
        time.sleep(1)
        st.toast("Done!", icon='🎉')
        time.sleep(0.5)
        st.success("Redirecting to dashboard...")
        time.sleep(0.5)
        st.session_state.current_page = 'dashboard'
        st.rerun()

    # Edit default schedule
    st.write("")
    st.write("")
    st.write("Want to edit your schedule?")
    if st.button("Edit Default Schedule"):
        st.session_state.current_page = 'edit_default_schedule'
        st.rerun()


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
elif st.session_state.current_page == 'edit_default_schedule':
    edit_default_schedule_page()
elif st.session_state.current_page == 'edit_profile':
    edit_profile_page()

# Feature to add:
# -> Actual data in the dashboard (Done)
# -> Create Admin Dashboard (in-progress)
# -> Mail the timesheet to the admin when user clicks submit
# -> Send the confirmation email to the user when they submit
# -> Disable the already submitted time sheets
# -> Use an actual database
# -> Cookies for login
# -> Add some more elements in the StandardUser class to display in the dashboard (DONE)
# -> Add the ability to edit the default schedule (DONE)
# -> Add a back button to all pages (NOT NEEDED)
# -> Add a dashboard button to all pages (DONE)
# -> Design the Admin Dashboard (DONE)
# -> OTP for registration (DONE)
# -> Only msu.edu email addresses allowed (DONE)
# -> Only Mae and Julia can be admins (DONE)

