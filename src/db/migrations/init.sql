CREATE TABLE IF NOT EXISTS users
(
    id            INTEGER UNIQUE,
    lang          TEXT,
    access_token  TEXT,
    image_base_64 TEXT,
    last_flower   TEXT,
    longitude     FLOAT,
    latitude      FLOAT
);
