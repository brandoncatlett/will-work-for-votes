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

# Clear all votes from the database
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
    finally:
        # Close the database connection
        if conn:
            conn.close()


if __name__ == '__main__':
    # Create a database connection
    conn = create_connection()
    # Clear all votes from the database
    clear_votes(conn)
    # Reset the database
    #reset_database(conn)
    #delete_columns(conn)
    recreate_table(conn)
    # Close the database connection
    conn.close()