import streamlit as st
import requests
import os
from datetime import datetime

def export_error_to_file(error_message):
    with open("error_log.txt", "a") as f:
        f.write(f"[{datetime.now()}] {error_message}\n")

def check_username_availability(username):
    try:
        response = requests.get(f"https://www.instagram.com/{username}/")
        return response.status_code == 404
    except Exception as e:
        export_error_to_file(str(e))
        return False

def login_and_grab_user_id(username, password):
    try:
        url = "https://www.instagram.com/accounts/login/ajax/"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "X-CSRFToken": "missing"
        }
        data = {
            "username": username,
            "enc_password": f"#PWD_INSTAGRAM_BROWSER:0:{int(datetime.now().timestamp())}:{password}"
        }
        response = requests.post(url, headers=headers, data=data)
        response_data = response.json()

        if response_data.get("authenticated"):
            user_id = response_data.get("userId", "")
            return user_id
        else:
            raise ValueError("Invalid credentials or login failed.")
    except Exception as e:
        export_error_to_file(str(e))
        st.error("Login failed.")
        return None

def attempt_to_claim_username(account_id, username):
    try:
        url = f"https://accountscenter.instagram.com/profiles/{account_id}/username/"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }
        data = {"username": username}
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return True
        else:
            raise ValueError(f"Failed to claim username: {response.status_code}")
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

def test_script():
    test_usernames = ["available_name", "taken_name", "bannedusername"]
    test_username = "test_user"
    test_password = "test_pass"
    test_user_id = "12345678"
    st.write("Simulating login...")
    user_id = login_and_grab_user_id(test_username, test_password)
    if user_id:
        st.write(f"Login successful. User ID: {user_id}")
    else:
        st.write("Login failed during test.")
    for uname in test_usernames:
        if uname in banned_usernames:
            st.write(f"Skipping banned username: {uname}")
            continue
        available = check_username_availability(uname)
        st.write(f"Username '{uname}' availability: {available}")
    test_claim_username = "available_name"
    if test_claim_username not in banned_usernames and check_username_availability(test_claim_username):
        st.write(f"Attempting to claim username: {test_claim_username}")
        success = attempt_to_claim_username(test_user_id, test_claim_username)
        if success:
            st.write(f"Successfully claimed username: {test_claim_username}")
        else:
            st.write(f"Failed to claim username: {test_claim_username}")
test_script()
