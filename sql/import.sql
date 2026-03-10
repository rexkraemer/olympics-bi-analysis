COPY athletes FROM '/home/rex/olympics-bi-analysis/data/athletes.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
COPY countries FROM '/home/rex/olympics-bi-analysis/data/countries.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
COPY events FROM '/home/rex/olympics-bi-analysis/data/events.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');

COPY athlete_event(athlete_id, event_id, year, medal, age, height, weight, noc)
	FROM '/home/rex/olympics-bi-analysis/data/athlete_event.csv' 
	WITH (FORMAT csv, HEADER true, DELIMITER ',');
