from flask import Flask
import sqlite3
from sqlite3 import Error


# Path to the database
dbPath = '/Users/brandoncatlett/PycharmProjects/will-work-for-votes/src/Database/votes.db'


# Delete columns from a table
def delete_columns(conn):
    # Check if conn is a valid SQLite connection object
    if not isinstance(conn, sqlite3.Connection):
        print("Invalid connection object.")
        return

    try:
        # Create a new table without the first_name and last_name columns
        sql_create_new_table = """ CREATE TABLE IF NOT EXISTS new_slack_users (
                                    id INTEGER PRIMARY KEY,
                                    remaining_votes INTEGER DEFAULT 3,
                                    votes_received INTEGER DEFAULT 0
                                ); """
        c = conn.cursor()
        c.execute(sql_create_new_table)

        # Copy the data from the old table to the new one
        c.execute("INSERT INTO new_slack_users SELECT id, remaining_votes, votes_received FROM slack_users;")

        # Drop the old table
        c.execute("DROP TABLE slack_users;")

        # Rename the new table to the original name
        c.execute("ALTER TABLE new_slack_users RENAME TO slack_users;")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

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

app = Flask(__name__)


# Reset the Votes_Receieved for all users to 0
def reset_votes_received(conn):
    # Check if conn is a valid SQLite connection object
    if not isinstance(conn, sqlite3.Connection):
        print("Invalid connection object.")
        return

    try:
        cur = conn.cursor()
        # Update the votes_received for all users to 0
        cur.execute("UPDATE slack_users SET votes_received = 0")
        conn.commit()

        # Verify that the votes_received value for all users has been updated to 0
        cur.execute("SELECT votes_received FROM slack_users")
        votes = cur.fetchall()
        if all(vote[0] == 0 for vote in votes):
            print('All votes_received have been reset to 0 for all users.')
        else:
            print("Error: Not all votes_received values were updated correctly.")
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

# Clear all entries from the votes database
def clear_votes(conn):
    try:
        cur = conn.cursor()
        # Count the number of records before deletion
        cur.execute("SELECT COUNT(*) FROM votes")
        count_before = cur.fetchone()[0]
        print(f"Number of records before deletion: {count_before}")

        # Delete the records
        print("Deleting records...")
        cur.execute("DELETE FROM votes")
        conn.commit()
        print("Records deleted.")

        # Count the number of records after deletion
        cur.execute("SELECT COUNT(*) FROM votes")
        count_after = cur.fetchone()[0]
        print(f"Number of records after deletion: {count_after}")

        # Verify that all records have been deleted
        if count_after == 0:
            print("All records have been successfully deleted.")
        else:
            print("Not all records were deleted. Please check the database.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Reset the database
def reset_database(conn):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM slack_users")
        conn.commit()
        print("Database reset successfully.")
    except Exception as e:
        print(f"An error occurred while resetting the database: {e}")


# Reset the votes remaining for all users
def reset_votes_remaining(conn, votecount):
    # Check if conn is a valid SQLite connection object
    if not isinstance(conn, sqlite3.Connection):
        raise ValueError("Invalid connection object.")

    try:
        cur = conn.cursor()
        # Update the remaining_votes for all users to 3
        cur.execute("UPDATE slack_users SET remaining_votes = ?", (votecount, ))
        conn.commit()

        # Check if the remaining_votes value for all users has been updated to 3
        cur.execute("SELECT remaining_votes FROM slack_users")
        votes = cur.fetchall()
        if all(vote[0] == 3 for vote in votes):
            print(f'All votes have been reset to 3 for all users.')
        else:
            print("Error: Not all remaining_votes values were updated correctly.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Delete columns from the slack_users table
def recreate_table(conn):
    # Check if conn is a valid SQLite connection object
    if not isinstance(conn, sqlite3.Connection):
        raise ValueError("Invalid connection object.")

    try:
        c = conn.cursor()

        # Drop the old table
        c.execute("DROP TABLE IF EXISTS slack_users;")

        # Create a new table with only necessary columns
        sql_create_new_table = """ CREATE TABLE slack_users (
                                    id TEXT PRIMARY KEY,
                                    remaining_votes INTEGER DEFAULT 3,
                                    votes_received INTEGER DEFAULT 0
                                ); """
        c.execute(sql_create_new_table)
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")


# Clear all entries from the slack_users table
def clear_slack_users(conn):
    # Check if conn is a valid SQLite connection object
    if not isinstance(conn, sqlite3.Connection):
        raise ValueError("Invalid connection object.")

    # Check if the connection is open
    if conn:
        try:
            cur = conn.cursor()
            # Count the number of records before deletion
            cur.execute("SELECT COUNT(*) FROM slack_users")
            count_before = cur.fetchone()[0]
            print(f"Number of records before deletion: {count_before}")

            # Delete the records
            print("Deleting records...")
            cur.execute("DELETE FROM slack_users")
            conn.commit()
            print("Records deleted.")

            # Count the number of records after deletion
            cur.execute("SELECT COUNT(*) FROM slack_users")
            count_after = cur.fetchone()[0]
            print(f"Number of records after deletion: {count_after}")

            # Verify that all records have been deleted
            if count_after == 0:
                print("All records have been successfully deleted.")
            else:
                print("Not all records were deleted. Please check the database.")
        except Exception as e:
            print(f"An error occurred: {e}")
    else:
        print("The database connection is closed.")


if __name__ == '__main__':
    # Create a database connection
    conn = create_connection()
    # Clear all votes from the database
    clear_votes(conn)
    # Reset the database
    reset_votes_remaining(conn, 5)
    reset_votes_received(conn)
    delete_columns(conn)
    recreate_table(conn)
    clear_slack_users(conn)
    # Close the database connection
    conn.close()