# Will Work For Votes

This project is a simple voting system for Slack users. It allows users to give votes to their peers, with each user having a maximum of 3 votes per calendar month. The system is implemented in Python using the Flask framework.

## Features

- Users can give votes to their peers.
- Each user has a maximum of 3 votes per calendar month.
- The system keeps track of the number of votes each user has received.
- At the start of each month, the system resets the vote count for each user and records the user who had the most votes in the previous month.

## Setup

### Dependencies

- Python 3.6+
- Flask
- APScheduler
- sqlite3
- slack_sdk

You can install the dependencies with pip:

```bash
pip install flask APScheduler sqlite3 slack_sdk
```

### Database

The system uses a SQLite database to store the votes and user information. The database file is located at `src/Database/votes.db`.

### Slack Bot

The system uses a Slack bot to send messages. You need to generate a Slack token and replace the placeholder in the `slack_client` variable in `src/Server/Server.py`.

```python
slack_client = WebClient(token='your-slack-token')
```

### Ngrok Server

The system uses ngrok to expose the local server to the internet. This allows the Slack bot to send HTTP requests to the local server. You need to install ngrok and run it on the same port as the Flask app.

```bash
ngrok http 5000
```

Then, you need to configure the Slack bot to send requests to the ngrok server.

## Usage

To run the system, navigate to the `src/Server` directory and run `Server.py`.

```bash
python Server.py
```

The system will start a Flask app on port 5000 and a background job to reset the votes at the start of each month.

To vote for a user, send a POST request to the `/niceTry` route with the `text` parameter set to the username of the user you want to vote for and the `user_name` parameter set to your username.

```bash
curl -X POST -d "text=username&user_name=your_username" http://localhost:5000/niceTry
```

The system will return a message indicating whether the vote was successful or not.
