import random
from flask import Flask, request, render_template, redirect, url_for, flash
import json
import os
import time
import requests
import threading
import urllib3

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
def check_instagram_username_exists(username):
    # List of proxies with different usernames, passwords, and host details
    proxies_list = [
        {
            "http": "http://brd-customer-hl_f0d25c59-zone-residential_proxy1:883zbumj1r1p@brd.superproxy.io:33335",
            "https": "https://brd-customer-hl_f0d25c59-zone-residential_proxy1:883zbumj1r1p@brd.superproxy.io:33335"
        },
        {
            "http": "http://brd-customer-hl_de20a170-zone-residential_proxy1:wxcp53p9mbzs@brd.superproxy.io:33335",
            "https": "https://brd-customer-hl_de20a170-zone-residential_proxy1:wxcp53p9mbzs@brd.superproxy.io:33335"
        },
        {
            "http": "http://brd-customer-hl_0a108a61-zone-residential_proxy1:omfu311fmszk@brd.superproxy.io:33335",
            "https": "https://brd-customer-hl_0a108a61-zone-residential_proxy1:omfu311fmszk@brd.superproxy.io:33335"
        },
        {
            "http": "http://brd-customer-hl_7fb69707-zone-residential_proxy1:d379rnk5pkut@brd.superproxy.io:33335",
            "https": "https://brd-customer-hl_7fb69707-zone-residential_proxy1:d379rnk5pkut@brd.superproxy.io:33335"
        }
    ]
    
    # Randomly choose a proxy from the list
    proxy = random.choice(proxies_list)
    
    # Instagram API URL and headers
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

    # Number of retries
    max_retries = 3
    retries = 0

    while retries < max_retries:
        try:
            proxy = random.choice(proxies_list)
            # Send the GET request using the chosen proxy
            response = requests.get(url, headers=headers, proxies=proxy, verify=False)
            
            # If the response status code is 404, the user doesn't exist
            if response.status_code == 404:
                return False, f"Instagram user '{username}' does not exist."
            
            # If it's any other status code (200, 500, etc.), treat it as user exists
            elif response.status_code == 200:
                return True, ""
            else:
                print(response.status_code)
                retries += 1
                if retries < max_retries:
                    # Retry if the error is other than 404
                    print(f"Attempt {retries} failed. Retrying...")
                else:
                    # Return error after max retries
                    return False, f"Error: Unable to verify username '{username}' . Please try again."
        
        except requests.exceptions.RequestException as e:
            retries += 1
            if retries < max_retries:
                # Retry on network errors
                print(f"Network error (attempt {retries}): {e}. Retrying...")
            else:
                return False, f"Error checking Instagram username after {max_retries} attempts: {e}"
    
    return False, "Max retries reached. Unable to verify username."

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Needed for flashing messages

CREDENTIALS_FILE = 'pushover_credentials.json'
FIXED_API_TOKEN = 'ap6a85f8fs81v1ox7hy2pp2akpseia'  # Fixed Pushover API token
threads = {}
threads_lock = threading.Lock()  # A lock to prevent race conditions when accessing the threads dictionary

def send_notification(message, user_key, priority=0):
    url = 'https://api.pushover.net/1/messages.json'
    data = {
        'user': user_key,
        'token': FIXED_API_TOKEN,
        'message': message,
        'priority': priority  # Adding the priority parameter
    }
    response = requests.post(url, data=data)
    return response.json()
def get_instagram_follow_counts(username):
    # List of proxies with different usernames, passwords, and host details
    proxies_list = [
        {
            "http": "http://brd-customer-hl_f0d25c59-zone-residential_proxy1:883zbumj1r1p@brd.superproxy.io:33335",
            "https": "https://brd-customer-hl_f0d25c59-zone-residential_proxy1:883zbumj1r1p@brd.superproxy.io:33335"
        },
        {
            "http": "http://brd-customer-hl_de20a170-zone-residential_proxy1:wxcp53p9mbzs@brd.superproxy.io:33335",
            "https": "https://brd-customer-hl_de20a170-zone-residential_proxy1:wxcp53p9mbzs@brd.superproxy.io:33335"
        },{
    "http": "http://brd-customer-hl_0a108a61-zone-residential_proxy1:omfu311fmszk@brd.superproxy.io:33335",
    "https": "https://brd-customer-hl_0a108a61-zone-residential_proxy1:omfu311fmszk@brd.superproxy.io:33335"
},{
    "http": "http://brd-customer-hl_7fb69707-zone-residential_proxy1:d379rnk5pkut@brd.superproxy.io:33335",
    "https": "https://brd-customer-hl_7fb69707-zone-residential_proxy1:d379rnk5pkut@brd.superproxy.io:33335"
}

    ]

    # Randomly choose a proxy from the list
    proxy = random.choice(proxies_list)

    # Instagram API URL and headers
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
        # Send the GET request using the chosen proxy
        response = requests.get(url, headers=headers, params=params, proxies=proxy, verify=False)
        response.raise_for_status()
        
        # Parse the JSON response
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
    # Ensure thread is only printed once when it starts
    thread_name = threading.current_thread().name
    

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
                    print(username)
            else:
                send_notification(f"First time checking. Current followers count: {current_followers}", user_key)
            write_current_followers(file_path, current_followers)
        else:
            send_notification("Failed to get current followers count.", user_key,-1)
            continue
        # Ensure we wait for 10 seconds before the next check
        time.sleep(600)  # Wait for 10 seconds before checking again

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        user_key = request.form['user_key']

        # Check if the username exists by querying the Instagram API
        exists, error_message = check_instagram_username_exists(username)

        if not exists:
            flash(error_message, "error")
            return redirect(url_for('index'))

        with threads_lock:
            # Check if the username is already being monitored
            if username in threads and threads[username].is_alive():
                flash(f"The username {username} is already being monitored.", "error")
                return redirect(url_for('index'))

            # Save the user details only if the username exists
            save_pushover_credentials(username, user_key)
            
            output_dir = 'uname'
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Run the function in a background thread
            thread = threading.Thread(target=check_followers_change, args=(username, output_dir), name=f"Monitor-{username}")
            threads[username] = thread
            thread.start()
        
        flash(f"Started monitoring for {username}.", "success")
        send_notification(f"New User Registered ( {username} )", "u8ycu2qxyrtiyk8e6e6okvj6dhfreh",)
        return redirect(url_for('index'))
    return render_template('index.html')


def start_existing_threads():
    if os.path.exists(CREDENTIALS_FILE):
        with open(CREDENTIALS_FILE, 'r') as file:
            credentials = json.load(file)
        output_dir = 'uname'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Lock to ensure no race condition in starting threads
        with threads_lock:
            for username in credentials.keys():
                # Check if a thread for this username is already running
                if username not in threads or not threads[username].is_alive():
                    thread = threading.Thread(target=check_followers_change, args=(username, output_dir), name=f"Monitor-{username}")
                    threads[username] = thread
                    thread.start()

if __name__ == '__main__':
    start_existing_threads()  # Start monitoring for existing usernames when app starts
    app.run(debug=True, host='0.0.0.0', port=4000, use_reloader=False)  # Run on 0.0.0.0 and port 4000
