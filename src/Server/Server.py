from flask import Flask, request, jsonify
from slack_sdk import WebClient
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import certifi
import requests
import random
import ssl
import sqlite3
from sqlite3 import Error
from datetime import datetime

app = Flask(__name__)

ssl_context = ssl.create_default_context()
ssl_context.load_verify_locations(certifi.where())

# Path to the database
dbPath = '/Users/brandoncatlett/PycharmProjects/will-work-for-votes/src/Database/votes.db'
# Generate a slack bot to send messages
slack_client = WebClient(token='xoxb-7048517361889-7034007566838-I4CULnF0OdajSjKWyRtvehrw')


# Reset the votes on a background schedule
def reset_votes():
    conn = create_connection()
    cur = conn.cursor()

    # Find the user with the most votes_received
    cur.execute("SELECT id, MAX(votes_received) FROM slack_users")
    user, max_votes = cur.fetchone()
    print(f'User {user} had the most votes with a total of {max_votes} votes.')

    # Reset the votes
    cur.execute("UPDATE slack_users SET remaining_votes = 3, votes_received = 0")
    conn.commit()
    print(f'All votes have been reset to 3 for all users at {datetime.now()}')


scheduler = BackgroundScheduler()
scheduler.add_job(reset_votes, 'cron', day=1)
scheduler.start()

# Create a connection to the database
def create_connection():
    conn = None;
    try:
        conn = sqlite3.connect(dbPath)
        print(sqlite3.version)
    except Error as e:
        print(e)
    if conn:
        return conn


# Create a table in the database
def create_table(conn):
    try:
        sql_create_slack_users_table = """ CREATE TABLE IF NOT EXISTS slack_users (
                                            id INTEGER PRIMARY KEY,
                                            remaining_votes INTEGER DEFAULT 3,
                                            votes_received INTEGER DEFAULT 0
                                        ); """
        c = conn.cursor()
        c.execute(sql_create_slack_users_table)
    except Error as e:
        print(e)


# Add a new user to the database
def add_new_user(conn, username):
    """
    Add a new user to the slack_users table
    :param conn: Connection object
    :param user_id: The ID of the new user
    """
    sql = ''' INSERT INTO slack_users(id, remaining_votes, votes_received)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    # The new user starts with 3 remaining votes and 0 votes received
    cur.execute(sql, (username, 3, 0))  # No need to convert user_id to int
    conn.commit()


# Check if a user can vote
def can_vote(conn, user, voter):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM votes WHERE voter=? AND date=?", (voter, datetime.now().strftime('%Y-%m')))
    votes = cur.fetchone()[0]
    return votes < 3 and user != voter


# Add a vote to the database
def add_vote(conn, user, voter):
    if can_vote(conn, user, voter):
        cur = conn.cursor()
        cur.execute("INSERT INTO votes(user,voter,date) VALUES(?,?,?)", (user, voter, datetime.now().strftime('%Y-%m')))
        conn.commit()
        return True
    return False


# Decrement the remaining_votes value for a voter
def decrement_remaining_votes(conn, voter):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE slack_users SET remaining_votes = remaining_votes - 1 WHERE id=?", (voter,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


# Process a vote
def process_vote(user, voter):
    conn = create_connection()
    message = None
    success = False

    # Check if the voter is voting for themselves
    if user == voter:
        print("Voter is trying to vote for themselves.")
        return False, 'You cannot vote for yourself.'

    # Check if the voter has any remaining votes
    cur = conn.cursor()
    # Print all ids in the slack_users table
    cur.execute("SELECT id FROM slack_users")
    ids = cur.fetchall()
    print(f"All ids in the slack_users table: {ids}")
    # Use the TRIM() function to remove whitespace from the voter value and the id in the slack_users table
    cur.execute("SELECT remaining_votes FROM slack_users WHERE TRIM(id)=?", (voter.strip(),))
    row = cur.fetchone()
    if row is None:
        print("Voter does not exist.")
        return False, 'Voter does not exist.'
    remaining_votes = row[0]
    if remaining_votes <= 0:
        print("Voter has no remaining votes.")
        return False, 'You have no remaining votes.'

    # Check if the voter is a member of the correct channel
    response = slack_client.conversations_members(channel='C070V6LELJJ')
    members = response["members"]
    if voter not in members:
        print("Voter is not a member of the correct channel.")
        return False, 'You are not a member of the correct channel.'

    if add_vote(conn, user, voter):
        # Increment the votes_received value for the user
        increment_votes_received(conn, user)

        # Decrement the remaining_votes value for the voter
        decrement_remaining_votes(conn, voter)

        # List of possible messages
        messages = [
            f'{user}! Someone thinks you are doing a great job!',
            f'Great work, {user}! You got a vote!',
            f'Keep it up, {user}! Someone appreciated your work!',
            f'Well done, {user}! You received a vote!'
        ]
        # Select a random message from the list
        message = random.choice(messages)

        success = True
    else:
        print("add_vote() returned False.")
    conn.close()
    return success, message


# Increment the votes received for a user
# That's how you win!
def increment_votes_received(conn, username):
    # Check if conn is a valid SQLite connection object
    if not isinstance(conn, sqlite3.Connection):
        raise ValueError("Invalid connection object.")

    try:
        cur = conn.cursor()
        # Retrieve the current votes_received value
        cur.execute("SELECT votes_received FROM slack_users WHERE id=?", (username,))
        votes_received_before = cur.fetchone()[0]

        # Increment the votes_received value
        cur.execute("UPDATE slack_users SET votes_received = votes_received + 1 WHERE id=?", (username,))
        conn.commit()

        # Check if the votes_received value has been incremented correctly
        cur.execute("SELECT votes_received FROM slack_users WHERE id=?", (username,))
        votes_received_after = cur.fetchone()[0]
        if votes_received_after == votes_received_before + 1:
            print(f'votes_received value for user {username} has been incremented correctly.')
        else:
            print("Error: votes_received value was not incremented correctly.")
    except Exception as e:
        print(f"An error occurred: {e}")


# root route handling
@app.route('/', methods=['POST'])
def root():
    return vote()


# vote route handling
@app.route('/niceTry', methods=['POST'])
def vote():
    conn = create_connection()
    username = request.form.get('text')
    voter = request.form.get('user_name')

    # Data validation
    if not username or not isinstance(username, str):
        return jsonify(response_type='ephemeral', channel='C070V6LELJJ', text='Invalid username.'), 400
    if not voter or not isinstance(voter, str):
        return jsonify(response_type='ephemeral', channel='C070V6LELJJ', text='Invalid voter.'), 400

    # Check if the user exists in the slack_users table
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM slack_users WHERE id=?", (username,))
    user_exists = cur.fetchone()[0] > 0

    # If the user doesn't exist, add them to the slack_users table
    if not user_exists:
        add_new_user(conn, username)

    try:
        success, message = process_vote(username, voter)
        if not success:
            raise ValueError('Vote processing failed.')
    except ValueError as e:
        print(e)
        # Handle the error as needed
        conn.close()
        return jsonify(response_type='ephemeral', text=str(e)), 400
    else:
        if success:
            # Send a message to a specific channel
            conn.close()
            return jsonify(channel='C070V6LELJJ', text=message), 200
        else:
            conn.close()
            return jsonify(response_type='ephemeral', text='You cannot vote at this time.'), 200


if __name__ == '__main__':
    conn = create_connection()
    create_table(conn)
    app.run(port=5000, debug=True)