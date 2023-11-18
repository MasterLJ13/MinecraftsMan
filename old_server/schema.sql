DROP TABLE IF EXISTS teams;
CREATE TABLE IF NOT EXISTS teams (
    id integer PRIMARY KEY,
    color text NOT NULL
);

DROP TABLE IF EXISTS users;
CREATE TABLE IF NOT EXISTS users (
    id integer PRIMARY KEY AUTOINCREMENT,
    name text NOT NULL,
    team_id integer NOT NULL,
    FOREIGN KEY (team_id) REFERENCES teams (id)
);

DROP TABLE IF EXISTS splatzones;
CREATE TABLE IF NOT EXISTS splatzones (
    id integer PRIMARY KEY AUTOINCREMENT,
    owner_id integer,
    pos_long REAL NOT NULL,
    pos_lat REAL NOT NULL,
    osm_id integer,
    FOREIGN KEY (owner_id) REFERENCES users (id)
);