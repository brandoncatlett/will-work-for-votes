CREATE TABLE IF NOT EXISTS slack_users (
       id INTEGER PRIMARY KEY,
       first_name TEXT NOT NULL,
       last_name TEXT NOT NULL,
       remaining_votes INTEGER DEFAULT 3,
       votes_received INTEGER DEFAULT 0
);