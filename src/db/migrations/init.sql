CREATE TABLE IF NOT EXISTS users
(
    id           INTEGER UNIQUE,
    language     TEXT,
    access_token TEXT
);
