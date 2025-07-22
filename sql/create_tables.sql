CREATE TABLE check_post_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stop_datetime DATETIME,
    country_name TEXT,
    driver_gender TEXT,
    driver_age INTEGER,
    driver_race TEXT,
    violation TEXT,
    search_conducted BOOLEAN,
    search_type TEXT,
    stop_outcome TEXT,
    is_arrested BOOLEAN,
    stop_duration TEXT,
    drugs_related_stop BOOLEAN,
    stop_hour INTEGER,
    stop_month INTEGER,
    is_night_stop BOOLEAN
);

-- Dummy Reference Table Example
CREATE TABLE officers (
    officer_id INTEGER PRIMARY KEY,
    name TEXT,
    post_location TEXT,
    shift_time TEXT
);

CREATE TABLE vehicles (
    vehicle_number TEXT PRIMARY KEY,
    owner_id TEXT,
    type TEXT,
    flagged_status BOOLEAN
);

CREATE TABLE violations (
    violation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_number TEXT,
    violation_type TEXT,
    fine_amount INTEGER
);
