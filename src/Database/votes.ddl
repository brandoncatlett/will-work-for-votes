CREATE TABLE IF NOT EXISTS slack_users (
                                           id TEXT PRIMARY KEY,
                                           remaining_votes INTEGER DEFAULT 3,
                                           votes_received INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS votes (
                                     vote_id INTEGER PRIMARY KEY,
                                     user_id TEXT NOT NULL,
                                     voter_id TEXT NOT NULL,
                                     vote_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                                     FOREIGN KEY(user_id) REFERENCES slack_users(id),
    FOREIGN KEY(voter_id) REFERENCES slack_users(id)
    );