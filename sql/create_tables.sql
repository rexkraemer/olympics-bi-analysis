
-- Tabellen
CREATE TABLE athletes (
    athlete_id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    sex CHAR(1)
);

CREATE TABLE countries (
    noc CHAR(3) PRIMARY KEY,
    country VARCHAR(255)
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    sport VARCHAR(255),
    event VARCHAR(255)
);

CREATE TABLE athlete_event (
    athlete_id INT REFERENCES athletes(athlete_id),
    event_id INT REFERENCES events(event_id),
    noc CHAR(3) REFERENCES countries(noc),
    year INT,
    age INT,
    height FLOAT,
    weight FLOAT,
    medal VARCHAR(10)
);