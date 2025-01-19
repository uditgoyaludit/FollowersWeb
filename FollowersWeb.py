import os
import random
import json
import requests
import time
import threading
from flask import Flask, request, render_template, redirect, url_for, flash
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Environment Variables
SECRET_KEY = os.getenv('FLASK_SECRET_KEY')
FIXED_API_TOKEN = os.getenv('PUSHOVER_API_TOKEN')
ADMIN_USER_KEY = os.getenv('PUSHOVER_ADMIN_USER')
PROXY_USERNAME = os.getenv('PROXY_USERNAME')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')
PROXY_HOST = os.getenv('PROXY_HOST')
PROXY_PORT = os.getenv('PROXY_PORT')

app = Flask(__name__)
app.secret_key = SECRET_KEY
CREDENTIALS_FILE = 'pushover_credentials.json'
threads = {}
threads_lock = threading.Lock()

# Function to get proxy from environment variables
def get_proxy():
    return {
        "http": f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}",
        "https": f"https://{PROXY_USERNAME}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}",
    }

def check_instagram_username_exists(username):
    proxies_list = [get_proxy()]
    
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    headers = {
        "User-Agent": "Instagram 155.0.0.37.107 Android",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "198387",
        "X-IG-WWW-Claim": "0",
        "Referer": "https://www.instagram.com/",
    }
    
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            proxy = random.choice(proxies_list)
            response = requests.get(url, headers=headers, proxies=proxy, verify=False)
            if response.status_code == 404:
                return False, f"Instagram user '{username}' does not exist."
            elif response.status_code == 200:
                return True, ""
            else:
                retries += 1
                if retries < max_retries:
                    print(f"Attempt {retries} failed. Retrying...")
                else:
                    return False, f"Error: Unable to verify username '{username}' . Please try again."
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries < max_retries:
                print(f"Network error (attempt {retries}): {e}. Retrying...")
            else:
                return False, f"Error checking Instagram username after {max_retries} attempts: {e}"

    return False, "Max retries reached. Unable to verify username."

def send_notification(message, user_key, priority=0):
    url = 'https://api.pushover.net/1/messages.json'
    data = {
        'user': user_key,
        'token': FIXED_API_TOKEN,
        'message': message,
        'priority': priority,
    }
    response = requests.post(url, data=data)
    return response.json()

def get_instagram_follow_counts(username):
    proxies_list = [get_proxy()]
    
    url = "https://i.instagram.com/api/v1/users/web_profile_info/"
    params = {"username": username}
    headers = {
        "User-Agent": "Instagram 155.0.0.37.107 Android",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "X-IG-App-ID": "936619743392459",
        "X-ASBD-ID": "198387",
        "X-IG-WWW-Claim": "0",
        "Referer": "https://www.instagram.com/",
    }

    try:
        proxy = random.choice(proxies_list)
        response = requests.get(url, headers=headers, params=params, proxies=proxy, verify=False)
        response.raise_for_status()
        
        data = response.json()
        followers_count = data['data']['user']['edge_followed_by']['count']
        following_count = data['data']['user']['edge_follow']['count']
        
        return followers_count, following_count
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None, None

def read_previous_followers(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            previous_followers = int(file.read().strip())
            return previous_followers
    except FileNotFoundError:
        return None
    except ValueError:
        print("Error reading previous followers count.")
        return None

def write_current_followers(file_path, followers):
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(followers))

def save_pushover_credentials(username, user_key):
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            credentials = json.load(file)
    else:
        credentials = {}
    
    credentials[username] = {'user_key': user_key}
    
    with open(CREDENTIALS_FILE, 'w') as file:
        json.dump(credentials, file)

def get_pushover_credentials(username):
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            credentials = json.load(file)
        return credentials.get(username)
    return None

def check_followers_change(username, output_dir):
    while True:
        credentials = get_pushover_credentials(username)
        if not credentials:
            print(f"No Pushover credentials found for username: {username}")
            return
        user_key = credentials['user_key']
        file_path = os.path.join(output_dir, f'{username}_followers.txt')
        previous_followers = read_previous_followers(file_path)
        current_followers, following = get_instagram_follow_counts(username)
        if current_followers is not None:
            if previous_followers is not None:
                if current_followers < previous_followers:
                    send_notification(f"( {username} ) Followers decreased: {current_followers-previous_followers})", user_key)
                elif current_followers > previous_followers:
                    send_notification(f"( {username} ) Followers increased: {current_followers-previous_followers})", user_key)
                else:
                    send_notification(f"( {username} ) No change: {current_followers} ,{previous_followers}",user_key,-1)
            else:
                send_notification(f"First time checking. Current followers count: {current_followers}", user_key)
            write_current_followers(file_path, current_followers)
        else:
            send_notification("Failed to get current followers count.", user_key,-1)
            continue
        time.sleep(600)  # Wait for 10 minutes before checking again

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        user_key = request.form['user_key']
        exists, error_message = check_instagram_username_exists(username)
        if not exists:
            flash(error_message, "error")
            return redirect(url_for('index'))
        
        with threads_lock:
            if username in threads and threads[username].is_alive():
                flash(f"The username {username} is already being monitored.", "error")
                return redirect(url_for('index'))
            save_pushover_credentials(username, user_key)
            output_dir = 'uname'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            thread = threading.Thread(target=check_followers_change, args=(username, output_dir), name=f"Monitor-{username}")
            threads[username] = thread
            thread.start()

        flash(f"Started monitoring for {username}.", "success")
        send_notification(f"New User Registered ( {username} )", ADMIN_USER_KEY)
        return redirect(url_for('index'))
    return render_template('index.html')

def start_existing_threads():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            credentials = json.load(file)
        output_dir = 'uname'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with threads_lock:
            for username in credentials.keys():
                if username not in threads or not threads[username].is_alive():
                    thread = threading.Thread(target=check_followers_change, args=(username, output_dir), name=f"Monitor-{username}")
                    threads[username] = thread
                    thread.start()

if __name__ == '__main__':
    start_existing_threads()
    app.run(debug=True, host='0.0.0.0', port=4000, use_reloader=False)
