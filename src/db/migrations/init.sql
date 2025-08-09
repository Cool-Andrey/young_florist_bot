CREATE TABLE IF NOT EXISTS users
(
    id           INTEGER UNIQUE,
    lang         TEXT,
    access_token TEXT
);
