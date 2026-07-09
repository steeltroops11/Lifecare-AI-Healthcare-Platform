# SQLite database layer with EHR, Doctor Notes, Audit Logs, Hashed Credentials, and Phase 4 Smart Recommendation tables
import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "data/healthcare.db"
USERS_JSON_PATH = "login/users.json"

def get_connection():
    """Create a connection to the SQLite database."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables, upgrade schemas, and migrate users with hashed passwords."""
    conn = get_connection()
    cursor = conn.cursor()

    # Create users table with EHR context columns (Priority 2)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY,
        password TEXT NOT NULL,
        role TEXT NOT NULL,
        name TEXT NOT NULL,
        patient_id TEXT,
        age INTEGER,
        blood_group TEXT,
        emergency_contact TEXT,
        weight_kg REAL,
        height_cm REAL,
        photo_url TEXT,
        allergies TEXT DEFAULT 'None Reported',
        medications TEXT DEFAULT 'None',
        family_history TEXT DEFAULT 'None',
        smoking TEXT DEFAULT 'Non-smoker',
        alcohol TEXT DEFAULT 'Occasional',
        prev_diseases TEXT DEFAULT 'None',
        vaccinations TEXT DEFAULT 'Up-to-date',
        google_id TEXT,
        profile_picture TEXT,
        auth_provider TEXT DEFAULT 'local',
        email_verified INTEGER DEFAULT 0,
        last_login TEXT
    )
    """)

    # Migrate existing users table to add new Google OAuth columns if they don't exist
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN google_id TEXT")
    except Exception: pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN profile_picture TEXT")
    except Exception: pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'local'")
    except Exception: pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN email_verified INTEGER DEFAULT 0")
    except Exception: pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
    except Exception: pass
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN immunocompromised INTEGER DEFAULT 0")
    except Exception: pass

    # Create predictions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_email TEXT NOT NULL,
        disease TEXT NOT NULL,
        risk REAL NOT NULL,
        prediction INTEGER NOT NULL,
        timestamp TEXT NOT NULL,
        inputs_json TEXT NOT NULL
    )
    """)

    # Create appointments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_email TEXT NOT NULL,
        doctor_name TEXT NOT NULL,
        date_time TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Scheduled',
        hospital_name TEXT DEFAULT '',
        hospital_address TEXT DEFAULT '',
        specialty TEXT DEFAULT '',
        appointment_type TEXT DEFAULT 'request'
    )
    """)
    # Migrate existing appointments table to add new columns if not exist
    try:
        cursor.execute("ALTER TABLE appointments ADD COLUMN hospital_name TEXT DEFAULT ''")
    except Exception: pass
    try:
        cursor.execute("ALTER TABLE appointments ADD COLUMN hospital_address TEXT DEFAULT ''")
    except Exception: pass
    try:
        cursor.execute("ALTER TABLE appointments ADD COLUMN specialty TEXT DEFAULT ''")
    except Exception: pass
    try:
        cursor.execute("ALTER TABLE appointments ADD COLUMN appointment_type TEXT DEFAULT 'request'")
    except Exception: pass

    # Create notifications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        message TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        read INTEGER DEFAULT 0
    )
    """)

    # Create doctor_notes table (Priority 3)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS doctor_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_email TEXT NOT NULL,
        doctor_name TEXT NOT NULL,
        note TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
    """)

    # Create audit_logs table (Priority 6)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        action TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        details TEXT NOT NULL
    )
    """)

    # ---- Phase 4: Smart Recommendation System Tables ----

    # Drop removed/unwanted Phase 4 tables to clean database
    try:
        cursor.execute("DROP TABLE IF EXISTS recent_searches")
        cursor.execute("DROP TABLE IF EXISTS recommended_specialists")
    except Exception:
        pass

    # clinics_cache — stores Overpass API results to avoid repeated calls
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clinics_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        city_query TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        radius_km INTEGER DEFAULT 5,
        results_json TEXT NOT NULL,
        fetched_at TEXT NOT NULL
    )
    """)

    # favorites — patient saves preferred clinics
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_email TEXT NOT NULL,
        clinic_name TEXT NOT NULL,
        clinic_address TEXT DEFAULT '',
        clinic_lat REAL,
        clinic_lng REAL,
        added_at TEXT NOT NULL
    )
    """)

    # followups — medicine & follow-up reminders
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS followups (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_email TEXT NOT NULL,
        disease TEXT NOT NULL,
        due_date TEXT NOT NULL,
        reminder_type TEXT NOT NULL,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()

    # Prepopulate default users with hashed passwords if empty (Priority 7)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Default Admin Account
        cursor.execute("""
        INSERT INTO users (email, password, role, name, patient_id, age, blood_group, emergency_contact, weight_kg, height_cm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("admin@healthcare.com", generate_password_hash("admin123"), "Admin", "System Admin", None, None, None, None, None, None))
        
        # Default Doctor Account
        cursor.execute("""
        INSERT INTO users (email, password, role, name, patient_id, age, blood_group, emergency_contact, weight_kg, height_cm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("doctor@healthcare.com", generate_password_hash("doctor123"), "Doctor", "Dr. Navish", None, None, None, None, None, None))
        
        # Default Patient Account
        cursor.execute("""
        INSERT INTO users (email, password, role, name, patient_id, age, blood_group, emergency_contact, weight_kg, height_cm, allergies, medications, family_history, smoking, alcohol, prev_diseases, vaccinations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "patient@healthcare.com", 
            generate_password_hash("patient123"), 
            "Patient", 
            "John Doe", 
            "P-JOHNDOE", 
            30, 
            "A+", 
            "+1 (555) 123-4567", 
            65.0, 
            168.0,
            "Penicillin, Peanuts",
            "Lisinopril 10mg",
            "Father: Diabetes, Uncle: Heart Disease",
            "Non-smoker",
            "Occasional",
            "Childhood Asthma",
            "Flu, COVID-19, Tdap"
        ))
        conn.commit()

    # Prepopulate mock appointments if none exist
    cursor.execute("SELECT COUNT(*) FROM appointments")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO appointments (patient_email, doctor_name, date_time, reason, status)
        VALUES (?, ?, ?, ?, ?)
        """, ("patient@healthcare.com", "Dr. Navish", "2026-07-06 10:00", "General Heart Checkup", "Scheduled"))
        cursor.execute("""
        INSERT INTO appointments (patient_email, doctor_name, date_time, reason, status)
        VALUES (?, ?, ?, ?, ?)
        """, ("patient@healthcare.com", "Dr. Sarah Jenkins", "2026-07-08 14:30", "Kidney Function Consult", "Scheduled"))
        conn.commit()

    # Prepopulate mock notifications
    cursor.execute("SELECT COUNT(*) FROM notifications")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO notifications (user_email, message, timestamp, read)
        VALUES (?, ?, ?, ?)
        """, ("patient@healthcare.com", "Welcome to Lifecare Analytics System!", datetime.now().strftime("%Y-%m-%d %H:%M"), 0))
        cursor.execute("""
        INSERT INTO notifications (user_email, message, timestamp, read)
        VALUES (?, ?, ?, ?)
        """, ("doctor@healthcare.com", "System Initialized Successfully.", datetime.now().strftime("%Y-%m-%d %H:%M"), 0))
        conn.commit()

    # Prepopulate mock doctor notes (Priority 3)
    cursor.execute("SELECT COUNT(*) FROM doctor_notes")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO doctor_notes (patient_email, doctor_name, note, timestamp)
        VALUES (?, ?, ?, ?)
        """, ("patient@healthcare.com", "Dr. Navish", "Patient improving. Continue current cardiovascular medication. Advise next checkup in 1 month.", datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()

    # Prepopulate mock audit logs (Priority 6)
    cursor.execute("SELECT COUNT(*) FROM audit_logs")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO audit_logs (user_email, action, timestamp, details)
        VALUES (?, ?, ?, ?)
        """, ("system", "DATABASE_INIT", datetime.now().strftime("%Y-%m-%d %H:%M"), "Relational schema tables initialized."))
        conn.commit()

    conn.close()

# Auto-initialize database on import
init_db()

def get_user(email):
    """Retrieve user details by email."""
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def create_user(email, password, role, name):
    """Create a new user account with hashed password (Priority 7)."""
    conn = get_connection()
    cursor = conn.cursor()
    patient_id = "P-" + email.split("@")[0].upper() if role == "Patient" else None
    
    # Hash password if not pre-hashed
    hashed_pwd = password if password.startswith("pbkdf2:sha256:") else generate_password_hash(password)
    
    try:
        cursor.execute("""
        INSERT INTO users (email, password, role, name, patient_id, age, blood_group, emergency_contact, weight_kg, height_cm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (email, hashed_pwd, role, name, patient_id, 30 if role == "Patient" else None, "O+" if role == "Patient" else None, "", 70.0 if role == "Patient" else None, 170.0 if role == "Patient" else None))
        conn.commit()
        success = True
        add_audit_log(email, "USER_REGISTRATION", f"Created account role: {role}")
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def update_user_profile_ehr(email, age, blood_group, emergency_contact, weight, height, allergies, meds, fam_hist, smoking, alcohol, prev_dis, vaccs, immunocompromised=0):
    """Update patient demographic and EHR details (Priority 2)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE users
    SET age = ?, blood_group = ?, emergency_contact = ?, weight_kg = ?, height_cm = ?,
        allergies = ?, medications = ?, family_history = ?, smoking = ?, alcohol = ?, prev_diseases = ?, vaccinations = ?,
        immunocompromised = ?
    WHERE email = ?
    """, (age, blood_group, emergency_contact, weight, height, allergies, meds, fam_hist, smoking, alcohol, prev_dis, vaccs, int(immunocompromised), email))
    conn.commit()
    conn.close()
    add_audit_log(email, "PROFILE_UPDATE", "Updated demographics & Electronic Health Records (EHR).")

def clean_value(val, target_type):
    """Coerce a stored DB value to a Python primitive.

    Handles the legacy case where NumPy types were serialised by sqlite3 as
    raw ``bytes`` BLOBs. Falls back gracefully for any unexpected byte length
    instead of raising ``TypeError`` (which the previous inline version did).
    """
    if isinstance(val, bytes):
        import struct
        n = len(val)
        try:
            if target_type == 'float':
                if n == 4:
                    return struct.unpack('<f', val)[0]
                if n == 8:
                    return struct.unpack('<d', val)[0]
                # Unknown float width: treat the buffer as an integer-sized
                # float by re-interpreting via a same-width integer cast.
                if n in (1, 2):
                    return float(struct.unpack('<' + ('b' if n == 1 else 'h'), val)[0])
                if n >= 8:
                    return float(struct.unpack('<q', val[:8])[0])
                return 0.0
            else:  # int
                if n == 1:
                    return struct.unpack('<b', val)[0]
                if n == 2:
                    return struct.unpack('<h', val)[0]
                if n == 4:
                    return struct.unpack('<i', val)[0]
                if n >= 8:
                    return struct.unpack('<q', val[:8])[0]
                return 0
        except (struct.error, ValueError):
            # Last-resort: try to decode as an ascii/utf-8 number string.
            try:
                text = val.decode('utf-8', 'ignore').strip()
                return float(text) if target_type == 'float' else int(float(text))
            except (ValueError, UnicodeDecodeError):
                return 0.0 if target_type == 'float' else 0
    # Already a native type (or str / None) — coerce safely.
    try:
        return float(val) if target_type == 'float' else int(val)
    except (TypeError, ValueError):
        return 0.0 if target_type == 'float' else 0


def save_prediction(patient_email, disease, risk, prediction, inputs_dict, timestamp):
    """Save a prediction report into the database."""
    conn = get_connection()
    cursor = conn.cursor()

    # Cast numpy types or other types explicitly to Python primitives
    # to prevent sqlite3 from storing numpy types as bytes/BLOB
    risk_val = float(risk)
    pred_val = int(prediction)

    inputs_json = json.dumps(inputs_dict)
    cursor.execute("""
    INSERT INTO predictions (patient_email, disease, risk, prediction, timestamp, inputs_json)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (patient_email, disease, risk_val, pred_val, timestamp, inputs_json))
    conn.commit()
    conn.close()
    add_audit_log(patient_email, "DIAGNOSTIC_SCREENING", f"Disease: {disease}, Risk: {risk_val*100:.1f}%, Predict: {pred_val}")

def get_predictions(patient_email=None):
    """Retrieve predictions. If patient_email is None, get all predictions."""
    conn = get_connection()
    if patient_email:
        rows = conn.execute("SELECT * FROM predictions WHERE patient_email = ? ORDER BY timestamp DESC", (patient_email,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM predictions ORDER BY timestamp DESC").fetchall()
    conn.close()

    results = []
    for r in rows:
        d = dict(r)
        d["risk"] = clean_value(d["risk"], 'float')
        d["prediction"] = clean_value(d["prediction"], 'int')
        results.append(d)
    return results

def get_appointments(patient_email=None):
    """Retrieve appointments for a user."""
    conn = get_connection()
    if patient_email:
        rows = conn.execute("SELECT * FROM appointments WHERE patient_email = ? ORDER BY date_time ASC", (patient_email,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM appointments ORDER BY date_time ASC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_appointment(patient_email, doctor_name, date_time, reason):
    """Add a new scheduled appointment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO appointments (patient_email, doctor_name, date_time, reason, status)
    VALUES (?, ?, ?, ?, 'Scheduled')
    """, (patient_email, doctor_name, date_time, reason))
    conn.commit()
    conn.close()
    add_audit_log(patient_email, "APPOINTMENT_CREATE", f"Requested appointment with {doctor_name} for '{reason}'.")

def update_appointment_status(appointment_id, status):
    """Accept, Decline or complete an appointment."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE appointments SET status = ? WHERE id = ?
    """, (status, appointment_id))
    conn.commit()
    conn.close()
    
    # Audit log
    conn_audit = get_connection()
    appt = conn_audit.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,)).fetchone()
    conn_audit.close()
    if appt:
        add_audit_log(appt["patient_email"], "APPOINTMENT_STATUS_CHANGE", f"Appointment status changed to: {status}")

# ---- DOCTOR NOTES (Priority 3) ----
def create_doctor_note(patient_email, doctor_name, note):
    """Add a new clinical note for a patient."""
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    INSERT INTO doctor_notes (patient_email, doctor_name, note, timestamp)
    VALUES (?, ?, ?, ?)
    """, (patient_email, doctor_name, note, timestamp))
    conn.commit()
    conn.close()
    add_audit_log(patient_email, "DOCTOR_NOTE_ADD", f"Clinical note appended by {doctor_name}.")

def get_doctor_notes(patient_email):
    """Retrieve all doctor notes for a patient."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM doctor_notes WHERE patient_email = ? ORDER BY timestamp DESC", (patient_email,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ---- AUDIT LOGS (Priority 6) ----
def add_audit_log(user_email, action, details):
    """Insert an action details inside the audit logs log table."""
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    INSERT INTO audit_logs (user_email, action, timestamp, details)
    VALUES (?, ?, ?, ?)
    """, (user_email, action, timestamp, details))
    conn.commit()
    conn.close()

def get_audit_logs():
    """Retrieve all audit logs recorded in SQLite."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ---- NOTIFICATIONS ----
def add_notification(user_email, message):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    INSERT INTO notifications (user_email, message, timestamp, read)
    VALUES (?, ?, ?, 0)
    """, (user_email, message, timestamp))
    conn.commit()
    conn.close()

def get_notifications(user_email):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM notifications WHERE user_email = ? ORDER BY timestamp DESC", (user_email,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def mark_notifications_as_read(user_email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE notifications SET read = 1 WHERE user_email = ?", (user_email,))
    conn.commit()
    conn.close()

# ---- ADMIN ----
def get_all_users():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()


# ============================================================
# PHASE 4 — SMART RECOMMENDATION SYSTEM HELPERS
# ============================================================

# ---- CLINICS CACHE ----
def cache_clinics(city_query, lat, lng, radius_km, results_json):
    """Cache Overpass API results for a city query."""
    import json
    conn = get_connection()
    cursor = conn.cursor()
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Remove old cache for same query
    cursor.execute("DELETE FROM clinics_cache WHERE city_query = ? AND radius_km = ?", (city_query, radius_km))
    cursor.execute("""
    INSERT INTO clinics_cache (city_query, latitude, longitude, radius_km, results_json, fetched_at)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (city_query, lat, lng, radius_km, json.dumps(results_json) if not isinstance(results_json, str) else results_json, fetched_at))
    conn.commit()
    conn.close()

def get_cached_clinics(city_query, radius_km=5):
    """Return cached clinic results if less than 24 hours old, else None."""
    import json
    from datetime import timedelta
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM clinics_cache WHERE city_query = ? AND radius_km = ? ORDER BY fetched_at DESC LIMIT 1",
        (city_query, radius_km)
    ).fetchone()
    conn.close()
    if row:
        row = dict(row)
        fetched_at = datetime.strptime(row["fetched_at"], "%Y-%m-%d %H:%M")
        if datetime.now() - fetched_at < timedelta(hours=24):
            try:
                return json.loads(row["results_json"])
            except Exception:
                return None
    return None


# ---- FAVORITES ----
def add_favorite(patient_email, clinic_name, clinic_address="", clinic_lat=None, clinic_lng=None):
    """Save a clinic to patient favorites."""
    conn = get_connection()
    cursor = conn.cursor()
    added_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    # Avoid duplicates
    existing = conn.execute(
        "SELECT id FROM favorites WHERE patient_email = ? AND clinic_name = ?",
        (patient_email, clinic_name)
    ).fetchone()
    if not existing:
        cursor.execute("""
        INSERT INTO favorites (patient_email, clinic_name, clinic_address, clinic_lat, clinic_lng, added_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_email, clinic_name, clinic_address, clinic_lat, clinic_lng, added_at))
        conn.commit()
    conn.close()

def remove_favorite(patient_email, clinic_name):
    """Remove a clinic from patient favorites."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE patient_email = ? AND clinic_name = ?", (patient_email, clinic_name))
    conn.commit()
    conn.close()

def get_favorites(patient_email):
    """Get all saved favorite clinics for a patient."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM favorites WHERE patient_email = ? ORDER BY added_at DESC",
        (patient_email,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---- FOLLOWUPS / REMINDERS ----
def add_followup(patient_email, disease, due_date, reminder_type, message):
    """Add a health follow-up reminder (medicine, exercise, test, consultation)."""
    conn = get_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute("""
    INSERT INTO followups (patient_email, disease, due_date, reminder_type, message, status, created_at)
    VALUES (?, ?, ?, ?, ?, 'pending', ?)
    """, (patient_email, disease, due_date, reminder_type, message, created_at))
    conn.commit()
    conn.close()

def get_followups(patient_email, status='pending'):
    """Get health follow-up reminders for a patient."""
    conn = get_connection()
    if status == 'all':
        rows = conn.execute(
            "SELECT * FROM followups WHERE patient_email = ? ORDER BY due_date ASC",
            (patient_email,)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM followups WHERE patient_email = ? AND status = ? ORDER BY due_date ASC",
            (patient_email, status)
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_followup_status(followup_id, status):
    """Mark a follow-up reminder as done, snoozed or cancelled."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE followups SET status = ? WHERE id = ?", (status, followup_id))
    conn.commit()
    conn.close()


# ---- EXTENDED APPOINTMENT CREATE (Phase 4) ----
def create_appointment_request(patient_email, doctor_name, date_time, reason,
                               hospital_name="", hospital_address="", specialty="", appointment_type="request"):
    """Create a new appointment request with optional hospital details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO appointments (patient_email, doctor_name, date_time, reason, status,
                              hospital_name, hospital_address, specialty, appointment_type)
    VALUES (?, ?, ?, ?, 'Scheduled', ?, ?, ?, ?)
    """, (patient_email, doctor_name, date_time, reason, hospital_name, hospital_address, specialty, appointment_type))
    conn.commit()
    conn.close()
    add_audit_log(patient_email, "APPOINTMENT_REQUEST", f"Appointment request: {reason} at {hospital_name or 'TBD'}.")


def clear_all_user_data(user_email=None):
    """Clear all user-generated data from the database.

    If user_email is provided, only that user's data is cleared.
    If user_email is None, ALL data across all users is wiped (admin reset).
    User accounts themselves are always preserved.

    Returns a dict mapping table name -> number of rows deleted.
    """
    conn = get_connection()
    cursor = conn.cursor()
    tables = [
        ("predictions", "patient_email"),
        ("appointments", "patient_email"),
        ("notifications", "user_email"),
        ("doctor_notes", "patient_email"),
        ("audit_logs", "user_email"),
        ("favorites", "patient_email"),
        ("followups", "patient_email"),
        ("clinics_cache", None),  # No user column — always full wipe
    ]
    deleted = {}
    for table_name, email_col in tables:
        try:
            if user_email and email_col:
                cursor.execute(f"DELETE FROM {table_name} WHERE {email_col} = ?", (user_email,))
            else:
                cursor.execute(f"DELETE FROM {table_name}")
            deleted[table_name] = cursor.rowcount
        except Exception:
            deleted[table_name] = 0
    conn.commit()
    conn.close()
    return deleted

