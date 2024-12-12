import streamlit as st
import requests
import os
from datetime import datetime

def export_error_to_file(error_message):
    with open("error_log.txt", "a") as f:
        f.write(f"[{datetime.now()}] {error_message}\n")

def check_username_availability(username):
    return username.lower() not in banned_usernames

def login_and_grab_user_id(username, password):
    try:
        if username and password:
            return "sample_non_fb_user_id"
        else:
            raise ValueError("Invalid credentials")
    except Exception as e:
        export_error_to_file(str(e))
        st.error("Login failed.")
        return None

def attempt_to_claim_username(account_id, username):
    try:
    
        if account_id and username:
            return True
        else:
            raise ValueError("Invalid account or username")
    except Exception as e:
        export_error_to_file(str(e))
        st.error("Failed to claim username.")
        return False
banned_usernames = {"admin", "test", "bannedusername"}  

st.title("Instagram Username Checker and Claimer")
username = st.text_input("Username/Email", placeholder="Enter your username or email")
password = st.text_input("Password", type="password", placeholder="Enter your password")
start_stop = st.button("Start/Stop")
status = st.empty()

def main():
    if start_stop:
        status.text("Verifying: Checking login status...")

        user_id = login_and_grab_user_id(username, password)
        if not user_id:
            status.text("Error: Login failed.")
            return

        status.text("Ready: Everything is good to go.")
        try:
            with open("usernames.txt", "r") as file:
                usernames = file.read().splitlines()
        except FileNotFoundError:
            export_error_to_file("usernames.txt not found.")
            st.error("Error: usernames.txt file not found.")
            return
        for uname in usernames:
            if uname.lower() in banned_usernames:
                continue

            available = check_username_availability(uname)
            if available:
                status.text(f"Attempting to claim username: {uname}")
                claimed = attempt_to_claim_username(user_id, uname)
                if claimed:
                    status.text(f"Success: Claimed username {uname}")
                    with open("claimed_accounts.txt", "a") as f:
                        f.write(f"{username}:{password}:{uname}\n")
                    break

        status.text("Stopped: Task completed.")

if __name__ == "__main__":
    main()
