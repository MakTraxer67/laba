CREATE TABLE IF NOT EXISTS user_roles (
    role_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    patronymic TEXT,
    login TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role_id INTEGER NOT NULL,
    FOREIGN KEY (role_id) REFERENCES user_roles (role_id)
);

CREATE TABLE IF NOT EXISTS medications (
    medication_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    form TEXT NOT NULL,
    manufacturer TEXT,
    UNIQUE (name, form)
);

CREATE TABLE IF NOT EXISTS prescriptions (
    prescription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    medication_id INTEGER NOT NULL,
    dosage TEXT NOT NULL,
    schedule_times TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    instructions TEXT,
    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES users (user_id),
    FOREIGN KEY (patient_id) REFERENCES users (user_id),
    FOREIGN KEY (medication_id) REFERENCES medications (medication_id)
);

CREATE TABLE IF NOT EXISTS intake_statuses (
    status_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS intake_records (
    intake_id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER NOT NULL,
    scheduled_at TEXT NOT NULL,
    status_id INTEGER NOT NULL DEFAULT 1,
    taken_at TEXT,
    comment TEXT,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions (prescription_id),
    FOREIGN KEY (status_id) REFERENCES intake_statuses (status_id),
    UNIQUE (prescription_id, scheduled_at)
);

CREATE INDEX IF NOT EXISTS idx_prescriptions_patient
    ON prescriptions (patient_id);

CREATE INDEX IF NOT EXISTS idx_intake_scheduled
    ON intake_records (scheduled_at);

INSERT OR IGNORE INTO user_roles (role_id, name) VALUES
    (1, 'Patient'),
    (2, 'Doctor'),
    (3, 'Administrator');

INSERT OR IGNORE INTO intake_statuses (status_id, name) VALUES
    (1, 'Planned'),
    (2, 'Taken'),
    (3, 'Skipped'),
    (4, 'Postponed');

