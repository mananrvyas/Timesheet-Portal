import hashlib
from StandardUser import StandardUser
from TimeSlot import TimeSlot
from datetime import datetime, timedelta
from PayPeriod import PayPeriod
from datetime import timedelta
import gradio as gr
import numpy as np
import time
import streamlit as st
import random


DEFAULT_SCHEDULE = {
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
        ['user1', hashlib.sha256('password1'.encode()).hexdigest(), 'admin', 'org1'],
        ['user2', hashlib.sha256('password2'.encode()).hexdigest(), 'user', 'org2']
    ]

if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'


def login_page():
    st.title("Sign In")
    st.subheader("Sign in to the Timesheet Portal")

    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    st.checkbox("Remember me")

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


def dashboard_page():
    st.title("User Dashboard")
    st.write(f"Welcome, {st.session_state.user_info['username']}")
    st.write("This is your dashboard.")


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
