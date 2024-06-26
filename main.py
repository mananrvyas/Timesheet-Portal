from StandardUser import StandardUser
from AdminUser import AdminUser
from TimeSlot import TimeSlot
from PayPeriod import PayPeriod
import datetime
import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt
import requests
import os
from dotenv import load_dotenv
import time
import extra_streamlit_components as stx
import mysql.connector as MySQL
import json

load_dotenv()
MAILGUN_API_KEY = os.getenv('MAILGUN_API_KEY')

ADMIN_PIN = os.getenv('ADMIN_PIN')

MAE_NETID = os.getenv('MAE_NETID')
JULIA_NETID = os.getenv('JULIA_NETID')

DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


def connect_to_db():
    """
    Establishes a connection to the MySQL database
    :return: connection object and cursor object
    """
    connection = MySQL.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    cursor = connection.cursor()
    return connection, cursor


def find_user_by_username(name: str) -> StandardUser or AdminUser:
    """
    Fetches a user from the database by their username
    :param name: the username of user
    :return: the user object
    """
    connection, cursor = connect_to_db()
    cursor.execute('''
        SELECT user_object, role
        FROM users
        WHERE username = %s
    ''', (name,))

    user_object, role = cursor.fetchone()

    if role == 'user':
        return StandardUser.deserialize(json.loads(user_object))
    elif role == 'admin':
        return AdminUser.deserialize(json.loads(user_object))
    else:
        return None


def fetch_all_users() -> list:
    """
    Fetches all users from the database
    :return: a list of all users
    """
    connection, cursor = connect_to_db()
    cursor.execute('''
        SELECT user_object, role
        FROM users
    ''')

    users = []
    for user_object, role in cursor.fetchall():
        if role == 'user':
            users.append(StandardUser.deserialize(json.loads(user_object)))
        elif role == 'admin':
            users.append(AdminUser.deserialize(json.loads(user_object)))

    return users


def update_user(user: StandardUser or AdminUser) -> None:
    """
    Updates a user in the database
    :param user: the user object
    :return: None
    """
    serialized_user = user.serialize()
    connection, cursor = connect_to_db()

    cursor.execute('''
        UPDATE users
        SET user_object = %s, password = %s
        WHERE username = %s
    ''', (json.dumps(serialized_user),user.get_password() ,user.username))

    connection.commit()


def create_user(user: StandardUser or AdminUser, role) -> None:
    """
    Creates a new user in the database
    :param user: the user object
    :param role: the role of the user
    :return: None
    """
    serialized_user = user.serialize()
    connection, cursor = connect_to_db()

    cursor.execute('''
        INSERT INTO users (username, password, user_object, role)
        VALUES (%s, %s, %s, %s)
    ''', (user.username, user.get_password(), json.dumps(serialized_user), role))

    connection.commit()


def find_role_by_username(name: str) -> str:
    """
    Fetches the role of a user by their username
    :param name:
    :return: their role
    """
    connection, cursor = connect_to_db()
    cursor.execute('''
        SELECT role
        FROM users
        WHERE username = %s
    ''', (name,))

    role = cursor.fetchone()[0]
    return role


st.set_page_config(page_title="Timesheet Portal", layout="centered")

# adding the default schedule (just for testing)
if 'DEFAULT_SCHEDULE' not in st.session_state:
    st.session_state.DEFAULT_SCHEDULE = {
        'Sunday': [],
        'Monday': [TimeSlot('01/03/23', '13:00', '17:00')],
        'Tuesday': [TimeSlot('01/04/23', '12:30', '16:00')],
        'Wednesday': [TimeSlot('01/05/23', '13:00', '17:00')],
        'Thursday': [TimeSlot('01/06/23', '12:30', '16:00')],
        'Friday': [TimeSlot('01/07/23', '15:00', '16:30')],
        'Saturday': []
    }

# fetching all users from the database
if 'USERS' not in st.session_state:
    st.session_state.USERS = fetch_all_users()

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'

# A list to keep track of the page history
if 'page_history' not in st.session_state:
    st.session_state.page_history = []


def login_page():
    """
    The login page
    :return:
    """
    cookie_manager = stx.CookieManager()

    username_cookie = cookie_manager.get("username")
    role_cookie = cookie_manager.get("role")
    user_info_cookie = {'username': username_cookie, 'role': role_cookie}

    if user_info_cookie['username']:
        st.session_state.user_info = user_info_cookie
        st.session_state.page_history.append(st.session_state.current_page)
        st.session_state.current_page = 'dashboard'
        st.rerun()

    st.title("Sign In")
    st.subheader("Sign in to the Timesheet Portal")
    st.write("For auto filling password, click on the password field, not the username field.")
    form = st.form(key='login_form')

    username = form.text_input("Username")
    password = form.text_input("Password", type='password')

    remember_me = form.checkbox("Remember me")

    if form.form_submit_button("Sign In"):
        # Authenticate user
        user = None
        for i in st.session_state.USERS:
            if i.username == username and i.get_password() == password:
                user = i
                break

        if user:
            st.session_state.user_info = {'username': user.username, 'role': find_role_by_username(user.username)}
            if remember_me:
                cookie_manager.set("username", user.username, key="username")
                cookie_manager.set("role", st.session_state.user_info['role'], key="role")

            st.session_state.page_history.append(st.session_state.current_page)
            st.session_state.current_page = 'dashboard'
            # print(st.session_state.user_info)
            st.rerun()
        else:
            st.error("Invalid Username or Password")

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
    user_list = [i.username for i in st.session_state.USERS]

    for i in range(0, 12):
        try:
            dummy_list[i] = user_list[i]
        except:
            continue

    if "admin_selected_user" not in st.session_state:
        st.session_state.admin_selected_user = None

    admin = None
    for i in st.session_state.USERS:
        if i.username == st.session_state.user_info['username']:
            admin = i
            break

    if admin is None:
        st.error("Turns out, you are not an admin ")
        return

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
            if i.username == st.session_state.admin_selected_user:
                admin_selected_user = i
                break
    except:
        pass

    st.write(" ")

    st.write(f"The users who require your attention are:")
    for i in st.session_state.USERS:
        for j in i._timesheets:
            if j['pay_period'].is_approved == 'pending':
                st.write(f"{i.username} - {j['pay_period'].get_start_date().strftime('%d %b %Y')}")

    if st.button("Logout"):
        st.session_state.current_page = 'login'
        st.rerun()

    st.write("--" * 15)

    if admin_selected_user is not None:
        # st.session_state.admin_selected_pay_period = None
        col1, col2 = st.columns(2)
        with col1:
            st.subheader(f"{admin_selected_user.username}\'s last 5 time sheets")
            df = create_timesheet_data(admin_selected_user.username)
            fig = plot_timesheet_bar_chart(df)
            st.pyplot(fig)


        with col2:
            st.subheader(f"{admin_selected_user.username}\'s Notifications")
            st.write("Click on the payperiod to view the timesheet and approve or reject it.")
            for i in admin_selected_user._timesheets:
                if i['pay_period'].is_approved == 'pending':
                    if st.button(f"Pay Period: {i['pay_period'].get_start_date().strftime('%d %b %Y')}"):
                        st.session_state.admin_selected_pay_period = i['pay_period']
                        st.rerun()
            st.write("")
            st.write("if you want to see more timesheets, click on the button below.")
            if st.button(f"View {admin_selected_user.username}'s all timesheets"):
                st.session_state.current_page = 'all_timesheets_admin'
                st.rerun()

    st.write("--" * 15)

    try:
        if st.session_state.admin_selected_pay_period is not None:
            st.subheader(f"{admin_selected_user.username}\'s Timesheet for the week of "
                         f"{st.session_state.admin_selected_pay_period.get_start_date().strftime('%d %b %Y')}")

            week1_timesheet, week2_timesheet = pretty_print_timesheet_v2(st.session_state.admin_selected_pay_period)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(week1_timesheet[0])
                for entry in week1_timesheet[1:]:
                    if entry:
                        if entry.startswith(" - "):
                            st.markdown(f"<div>{entry}</div>", unsafe_allow_html=True)
                        else:
                            st.write("")
                            st.markdown(f"<div><strong>{entry}</strong></div>", unsafe_allow_html=True)

            with col2:
                st.subheader(week2_timesheet[0])
                for entry in week2_timesheet[1:]:
                    if entry:
                        if entry.startswith(" - "):
                            st.markdown(f"<div>{entry}</div>", unsafe_allow_html=True)
                        else:
                            st.write("")
                            st.markdown(f"<div><strong>{entry}</strong></div>", unsafe_allow_html=True)
            st.write("")

            st.write("Total hours: ", st.session_state.admin_selected_pay_period.get_total_hours())

            def approve_or_reject(args):
                st.session_state.admin_selected_pay_period.is_approved = args
                if args == 'rejected':
                    st.toast("Rejecting the timesheet...")
                    time.sleep(1)
                    user = admin_selected_user
                    for i in user._timesheets:
                        if i['pay_period'] == st.session_state.admin_selected_pay_period:
                            i['pay_period'].is_approved = 'rejected'
                            break
                    update_user(user)
                    st.session_state.USERS = fetch_all_users()
                    st.toast("Timesheet Rejected!", icon='😔')
                else:
                    st.toast("Approving the timesheet...")
                    time.sleep(1)
                    user = admin_selected_user
                    for i in user._timesheets:
                        if i['pay_period'] == st.session_state.admin_selected_pay_period:
                            i['pay_period'].is_approved = 'rejected'
                            break
                    update_user(user)
                    st.session_state.USERS = fetch_all_users()
                    st.toast("Timesheet Approved!", icon='🎉')
                st.session_state.admin_selected_pay_period = None

            st.button('Approve', on_click=approve_or_reject, args=['approved'])
            st.button('Reject', on_click=approve_or_reject, args=['rejected'])

    except:
        pass


def pretty_print_timesheet_v2(pay_period):
    def week_of_date(date_str, format='%m/%d/%y'):
        date = datetime.datetime.strptime(date_str, format)
        start_of_week = date - datetime.timedelta(days=date.weekday())
        return start_of_week.strftime(format)

    timesheet = pay_period.get_timesheet_by_pay_period()
    sorted_dates = sorted(timesheet.keys(), key=lambda x: datetime.datetime.strptime(x, '%m/%d/%y'))

    start_date = datetime.datetime.strptime(pay_period.get_start_date().strftime('%m/%d/%y'), '%m/%d/%y')
    end_date = datetime.datetime.strptime(pay_period.get_end_date().strftime('%m/%d/%y'), '%m/%d/%y')
    midpoint_date = start_date + (end_date - start_date) / 2

    first_week_output = [f"Week of {week_of_date(sorted_dates[0])}"]
    second_week_output = [f"Week of {week_of_date(sorted_dates[len(sorted_dates) // 2])}"]

    for date_str in sorted_dates:
        current_date = datetime.datetime.strptime(date_str, '%m/%d/%y')
        week_output = first_week_output if current_date <= midpoint_date else second_week_output

        day_name = current_date.strftime('%A')
        week_output.append(f"{day_name} ({date_str}): {pay_period.get_total_hours_by_date(date_str)} hours")

        timeslots = timesheet[date_str]
        for slot in timeslots:
            start_time = slot.get_start().strftime('%H:%M')
            end_time = slot.get_end().strftime('%H:%M')
            week_output.append(f" - {start_time} to {end_time}")

        week_output.append("")

    return first_week_output, second_week_output


def create_timesheet_data(username):

    if 'current_week' not in st.session_state:
        st.session_state.current_week = datetime.date.today()
    user = None
    for i in st.session_state.USERS:
        if i.username == username:
            user = i
            break

    if user is None:
        st.error("User not found. Please contact the administrator (or create an account).")
        return

    time_sheets = user._timesheets[::-1]

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
    ax.set_ylim(0, 80)
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

    if find_role_by_username(user.username) == 'admin':
        st.session_state.current_page = 'admin_dashboard'
        st.rerun()

    col1, col2 = st.columns(2)

    with col1:
        current_time = datetime.datetime.now().strftime("%H:%M:%S")
        if "00:00:00" < current_time < "12:00:00":
            st.subheader(f"Good Morning, {user.fname if user.fname else user.username}")
        elif "12:00:00" < current_time < "17:00:00":
            st.subheader(f"Good Afternoon, {user.fname if user.fname else user.username}")
        else:
            st.subheader(f"Good Evening, {user.fname if user.fname else user.username}")
        image_url = "1"
        if user.photo:
            image_url = user.photo
        try:
            st.image(image_url, width=150)
        except:
            st.image("https://via.placeholder.com/150", width=150)

        if user.fname is None and user.lname is None:
            st.write("Click on edit profile to add your name.")
        else:
            st.write(f"Name: {user.fname if user.fname else ''} {user.lname if user.lname else ''}")
        st.write(f"Email: {user.email_address}")
        st.write(f"Phone: {user._phone_number if user._phone_number else ''}")
        st.write(f"{user.miscellaneous if user.miscellaneous else ''}")
        if st.button("Edit your profile"):
            st.session_state.current_page = 'edit_profile'
            st.rerun()
        if st.button("Edit default schedule"):
            st.session_state.current_page = 'edit_default_schedule'
            st.rerun()
        if st.button("Logout"):
            st.session_state.current_page = 'login'
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
        timesheet_df = create_timesheet_data(st.session_state.user_info['username'])
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
    st.write("Here, you can view all your past timesheets. and some stats as well (in the future)")

    if st.button("Back to Dashboard"):
        st.session_state.current_page = 'dashboard'
        st.rerun()

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
        st.subheader(f"{week_start.strftime('%A %d %b %Y')} to {week_end.strftime('%A %d %b %Y')}")

    with col3:
        if st.button('\>>'):
            st.session_state.current_week += datetime.timedelta(days=14)
            st.toast("Loading...")
            time.sleep(1)
            # st.toast("Done!", icon='🎉')
            st.rerun()

    user = None
    for i in st.session_state.USERS:
        if i.username == st.session_state.user_info['username']:
            user = i
            break

    if user is None:
        st.error("User not found. Please contact the administrator (or create an account).")
        return
    timesheets = user.get_timesheets()

    timesheet_found = False
    for i in timesheets:
        if str(i['pay_period'].get_start_date().strftime('%Y-%m-%d')) == str(week_start):
            timesheet_found = True
            pay_period = i['pay_period']

            week1_timesheet, week2_timesheet = pretty_print_timesheet_v2(pay_period)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(week1_timesheet[0])
                for entry in week1_timesheet[1:]:
                    if entry:
                        if entry.startswith(" - "):
                            st.markdown(f"<div>{entry}</div>", unsafe_allow_html=True)
                        else:
                            st.write("")
                            st.markdown(f"<div><strong>{entry}</strong></div>", unsafe_allow_html=True)

            with col2:
                st.subheader(week2_timesheet[0])
                for entry in week2_timesheet[1:]:
                    if entry:
                        if entry.startswith(" - "):
                            st.markdown(f"<div>{entry}</div>", unsafe_allow_html=True)
                        else:
                            st.write("")
                            st.markdown(f"<div><strong>{entry}</strong></div>", unsafe_allow_html=True)
            st.write("")

            st.write("Total hours: ", pay_period.get_total_hours())
            break

    if not timesheet_found:
        st.write("No timesheet found for this week.")


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

    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

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
        schedule = user._default_schedule
    else:
        st.error("User not found. Please contact the administrator (or try logging in again).")
        return

    disabled = False

    for i in user._timesheets:
        if i['pay_period'].get_start_date().strftime('%m/%d/%y') == week_start.strftime('%m/%d/%y'):
            disabled = True
            st.write("You have already submitted a timesheet for this week. You cannot make any changes.")
            break

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
            st.session_state[day][f"1_{day}_from_1"] = st.text_input(f"From", key=f"1_{day}_from_1", value=value,
                                                                     disabled=disabled)
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
            st.session_state[day][f"1_{day}_till_1"] = st.text_input(f"Till", key=f"1_{day}_till_1", value=value,
                                                                     disabled=disabled)
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
            st.session_state[day][f"1_{day}_from_2"] = st.text_input(f"From", key=f"1_{day}_from_2", value=value,
                                                                     disabled=disabled)
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
            st.session_state[day][f"1_{day}_till_2"] = st.text_input(f"Till", key=f"1_{day}_till_2", value=value,
                                                                     disabled=disabled)
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
            st.session_state[day][f"2_{day}_from_1"] = st.text_input(f"From", key=f"2_{day}_from_1", value=value,
                                                                     disabled=disabled)
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
            st.session_state[day][f"2_{day}_till_1"] = st.text_input(f"Till", key=f"2_{day}_till_1", value=value,
                                                                     disabled=disabled)
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
            st.session_state[day][f"2_{day}_from_2"] = st.text_input(f"From", key=f"2_{day}_from_2", value=value,
                                                                     disabled=disabled)
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
            st.session_state[day][f"2_{day}_till_2"] = st.text_input(f"Till", key=f"2_{day}_till_2", value=value,
                                                                     disabled=disabled)
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

    timeslots = []
    for i, day in enumerate(days):
        if st.session_state[day][f"1_{day}_from_1"] != '' and st.session_state[day][f"1_{day}_till_1"] != '':
            zz = (TimeSlot((week_start + datetime.timedelta(days=i)).strftime('%m/%d/%y'),
                           st.session_state[day][f"1_{day}_from_1"],
                           st.session_state[day][f"1_{day}_till_1"]))
            timeslots.append(zz)

        if st.session_state[day][f"1_{day}_from_2"] != '' and st.session_state[day][f"1_{day}_till_2"] != '':
            zz = (TimeSlot((week_start + datetime.timedelta(days=i)).strftime('%m/%d/%y'),
                           st.session_state[day][f"1_{day}_from_2"],
                           st.session_state[day][f"1_{day}_till_2"]))
            timeslots.append(zz)

        if st.session_state[day][f"2_{day}_from_1"] != '' and st.session_state[day][f"2_{day}_till_1"] != '':
            zz = (TimeSlot((week_start + datetime.timedelta(days=i + 7)).strftime('%m/%d/%y'),
                           st.session_state[day][f"2_{day}_from_1"],
                           st.session_state[day][f"2_{day}_till_1"]))
            timeslots.append(zz)

        if st.session_state[day][f"2_{day}_from_2"] != '' and st.session_state[day][f"2_{day}_till_2"] != '':
            zz = (TimeSlot((week_start + datetime.timedelta(days=i + 7)).strftime('%m/%d/%y'),
                           st.session_state[day][f"2_{day}_from_2"],
                           st.session_state[day][f"2_{day}_till_2"]))
            timeslots.append(zz)

    pay_period = PayPeriod(week_start.strftime('%m/%d/%y'))

    for i in timeslots:
        pay_period.add_timeslot(i)
    st.session_state.total_hours = pay_period.get_total_hours()

    pay_period = PayPeriod(week_start.strftime('%m/%d/%y'))

    st.write(f"Total Hours: ", round(st.session_state.total_hours, 1))

    if st.button("Submit", disabled=disabled):
        st.toast("Saving the timesheet...")
        time.sleep(1)
        st.toast("Mailing it to Mae and Julia...")

        senders_name = "Manan Vyas"
        senders_email = "timesheet-submission@mananvyas.in"
        subject = f"Timesheet Submission for {pay_period.get_start_date().strftime('%m/%d/%y')} to {pay_period.get_end_date().strftime('%m/%d/%y')}"
        message = (f"Hi Mae and Julia,\n"
                   f"Manan just submitted the timesheet for the week {pay_period.get_start_date().strftime('%m/%d/%y')} to {pay_period.get_end_date().strftime('%m/%d/%y')}\n\n"
                   f"Login to the dashboard to view, approve, or reject the timesheet.\n\n")

        user.submit_timesheet(pay_period, timeslots)
        update_user(user)
        st.session_state.USERS = fetch_all_users()
        week1 = ""
        for i in pretty_print_timesheet_v2(pay_period)[0]:
            week1 += i
            week1 += '\n'

        week2 = ""
        for i in pretty_print_timesheet_v2(pay_period)[1]:
            week2 += i
            week2 += '\n'

        message += f"Timesheet for Week 1:\n\n{week1}\n"
        message += f"Timesheet for Week 2:\n\n{week2}\n"

        message += f"Total Hours: {round(st.session_state.total_hours, 1)}\n\n"
        recipients = [f'{MAE_NETID}@msu.edu', f'{JULIA_NETID}@msu.edu']

        # print(message)

        # requests.post(
        #     "https://api.mailgun.net/v3/mananvyas.in/messages",
        #     auth=("api", MAILGUN_API_KEY),
        #     data={"from": f"{senders_name} <{senders_email}>",
        #           "to": [f"{recipients[0]}", f"{recipients[1]}"],
        #           "subject": f"{subject}",
        #           "text": f"{message}"})

        st.toast("Done!", icon='🎉')
        time.sleep(0.5)
        st.success("Timesheet submitted successfully!")
        time.sleep(0.8)
        st.success("Redirecting to dashboard...")
        time.sleep(1)
        st.session_state.current_page = 'dashboard'
        st.rerun()


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
        if i.username == username:
            st.error("Username already exists.")
            return

    if st.session_state.create_account_otp is None:
        if st.button("Send OTP"):
            st.session_state.create_account_otp = random.randint(1000, 9999)
            # print(st.session_state.create_account_otp)
            send_otp(username, st.session_state.create_account_otp, username + '@msu.edu', create_account=True)
            st.success(f"An OTP has been sent to your email address")
            time.sleep(1.3)
            st.rerun()
    else:
        otp = st.text_input("Enter OTP")
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
            elif otp != str(st.session_state.create_account_otp):
                st.error("Invalid OTP")
            else:
                if role == 'admin':
                    new_user = AdminUser(username, password, organization)
                elif role == 'user':
                    new_user = StandardUser(username, password, organization)
                create_user(new_user, role)
                st.session_state.USERS = fetch_all_users()
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

        st.write("Suddenly remembered your password? Click the button below to go back to the login page.")
        if st.button("Login"):
            st.session_state.current_page = 'login'
            st.rerun()

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
                return

        if email != "" and user is not None:
            if email != user.email_address:
                st.error("Email address does not match the records, contact Meow naan")
                return

        if st.button("Send OTP") and user is not None and email == user.email_address:
            st.session_state.otp = random.randint(1000, 9999)
            st.session_state.otp_sent = True
            send_otp(username, st.session_state.otp, email)
            st.success(f"An OTP has been sent to your email address")
            time.sleep(1.3)
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
                    user = None
                    for i in st.session_state.USERS:
                        if i.username == username:
                            user = i
                            break
                    if user is not None:
                        user.set_password(new_password)
                        update_user(user)
                        st.session_state.USERS = fetch_all_users()
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
        if mail == JULIA_NETID + '@msu.edu' or mail == MAE_NETID + '@msu.edu':
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
        if i.username == st.session_state.user_info['username']:
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

    if 'user_default_schedule' not in st.session_state:
        st.session_state.user_default_schedule = {}

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
        update_user(user)
        st.session_state.USERS = fetch_all_users()

        st.toast("Saving the default schedule...")
        time.sleep(1)
        st.toast("Done!", icon='🎉')
        time.sleep(0.5)
        st.success("Redirecting to dashboard...")
        time.sleep(0.5)
        st.session_state.current_page = 'dashboard'
        st.rerun()


def all_timesheets_admin(user: StandardUser):

    for i in st.session_state.USERS:
        if i.username == user:
            user = i
            break

    st.title(f" {user.username}'s Past Timesheets")
    st.write("Here, you can view all of their past timesheets. and some stats as well (in the future)")

    if st.button("Back to Dashboard"):
        st.session_state.current_page = 'dashboard'
        st.rerun()

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
        st.subheader(f"{week_start.strftime('%A %d %b %Y')} to {week_end.strftime('%A %d %b %Y')}")

    with col3:
        if st.button('\>>'):
            st.session_state.current_week += datetime.timedelta(days=14)
            st.toast("Loading...")
            time.sleep(1)
            # st.toast("Done!", icon='🎉')
            st.rerun()



    if user is None:
        st.error("User not found. Please contact the administrator (or create an account).")
        return
    timesheets = user.get_timesheets()

    timesheet_found = False
    for i in timesheets:
        if str(i['pay_period'].get_start_date().strftime('%Y-%m-%d')) == str(week_start):
            timesheet_found = True
            pay_period = i['pay_period']

            week1_timesheet, week2_timesheet = pretty_print_timesheet_v2(pay_period)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader(week1_timesheet[0])
                for entry in week1_timesheet[1:]:
                    if entry:
                        if entry.startswith(" - "):
                            st.markdown(f"<div>{entry}</div>", unsafe_allow_html=True)
                        else:
                            st.write("")
                            st.markdown(f"<div><strong>{entry}</strong></div>", unsafe_allow_html=True)

            with col2:
                st.subheader(week2_timesheet[0])
                for entry in week2_timesheet[1:]:
                    if entry:
                        if entry.startswith(" - "):
                            st.markdown(f"<div>{entry}</div>", unsafe_allow_html=True)
                        else:
                            st.write("")
                            st.markdown(f"<div><strong>{entry}</strong></div>", unsafe_allow_html=True)
            st.write("")

            st.write("Total hours: ", pay_period.get_total_hours())
            break

    if not timesheet_found:
        st.write("No timesheet found for this week.")


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
        if i.username == st.session_state.user_info['username']:
            user = i
            break
    if user is None:
        st.error("User not found. Please contact the administrator (or create an account).")
        return

    with col1:
        fname = st.text_input("First Name", value=user.fname)
        phone = st.text_input("Phone Number (Optional)", value=user._phone_number)
        photo_link = st.text_input("Photo URL", value=user.photo,
                                   help="Go to ASN website -> About -> People -> Right click on your photo -> "
                                        "Copy Image Address -> Paste here. (Or upload to imgur and paste the"
                                        " link here)")
    with col2:
        lname = st.text_input("Last Name", value=user.lname)
        misc_info = st.text_area("Miscellaneous Information", value=user.miscellaneous, height=122,
                                 help="It can be a quote, a short bio, etc.")

    if st.button("Save Changes"):
        if fname != '':
            user.fname = fname
        if lname != '':
            user.lname = lname
        if phone != '':
            user._phone_number = phone
        if photo_link != '':
            user.photo = photo_link
        if misc_info != '':
            user.miscellaneous = misc_info

        update_user(user)
        st.session_state.USERS = fetch_all_users()

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
#
#
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
elif st.session_state.current_page == 'all_timesheets_admin':
    all_timesheets_admin(st.session_state.admin_selected_user)
#
# # Feature to add:
# # -> Create Admin Dashboard (in-progress)
# # -> Mail the timesheet to the admin when user clicks submit
# # -> Send the confirmation email to the user when they submit
# # -> Disable the already submitted time sheets (DONE)
# # -> Use an actual database
# # -> Cookies for login
# # -> Add some more elements in the StandardUser class to display in the dashboard (DONE)
# # -> Add the ability to edit the default schedule (DONE)
# # -> Add a back button to all pages (NOT NEEDED)
# # -> Add a dashboard button to all pages (DONE)
# # -> Design the Admin Dashboard (DONE)
# # -> OTP for registration (DONE)
# # -> Only msu.edu email addresses allowed (DONE)
# # -> Only Mae and Julia can be admins (DONE)
# # -> Actual data in the dashboard (Done)
# # -> Notes for each day of timesheet
