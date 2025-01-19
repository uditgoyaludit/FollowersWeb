
# Instagram Followers Count Monitor 📊📱


A web application built with **Flask** to monitor Instagram followers count for a given user. It checks for changes in followers count and sends notifications via **Pushover**. The app supports multiple users and threading, making it easy to track followers for various Instagram accounts simultaneously.

---

## Features 🚀

- 📈 Monitor Instagram followers count for a given username.
- 🔔 Receive notifications on Pushover about followers count changes.
- 🔄 Handles multiple users simultaneously with threading.
- 🧑‍💻 Save Pushover credentials securely for each user.
- 🌐 Optional proxy configuration to avoid IP blocking.
- 🖥️ Web interface built using **Flask**.

---

## Tech Stack 💻

- **Backend:** Python 3.x, Flask
- **APIs:** Instagram API (web), Pushover API
- **Database:** JSON file storage for credentials
- **Libraries:** `requests`, `Flask`, `python-dotenv`, `threading`
- **Proxy:** Custom proxy configuration (optional)

---

## Screenshots 📸

![Screenshot 1](https://yourimagehost.com/screenshot1.png)

---

## Requirements 📋

1. **Python 3.x**
2. **Flask** for the web interface
3. **Requests** for HTTP requests
4. **Pushover** for notifications
5. **Python-dotenv** to load environment variables

---

## Installation & Setup 🛠️

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/instagram-followers-monitor.git
   cd instagram-followers-monitor
   ```

2. **Install dependencies:**

   Create and activate a virtual environment, then install the required dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Create `.env` file:**

   Create a `.env` file in the root of the project directory with the following content:

   ```bash
   FLASK_SECRET_KEY=<your_flask_secret_key>
   PUSHOVER_API_TOKEN=<your_pushover_api_token>
   PUSHOVER_ADMIN_USER=<your_pushover_admin_user_key>
   PROXY_USERNAME=<your_proxy_username>
   PROXY_PASSWORD=<your_proxy_password>
   PROXY_HOST=<your_proxy_host>
   PROXY_PORT=<your_proxy_port>
   ```

   Replace the placeholders with your actual values. If you are not using a proxy, you can leave the proxy variables blank.

4. **Run the Application:**

   To start the app, use the following command:

   ```bash
   python app.py
   ```

   The app will be running at `http://127.0.0.1:4000`.

---

## Usage 📲

1. Open the application in your browser.
2. Enter the Instagram username you want to monitor and your Pushover user key.
3. The system will start checking the followers count every 10 minutes and notify you if there's any change.

---

## Contributing 🤝

1. Fork this repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a pull request.

---

## License 📝

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements 🙏

- [Pushover](https://pushover.net/) for sending notifications.
- [Instagram API](https://developers.facebook.com/docs/instagram) for retrieving user data.
- [Flask](https://flask.palletsprojects.com/) for building the web app.
- [Requests](https://requests.readthedocs.io/) for handling HTTP requests.
