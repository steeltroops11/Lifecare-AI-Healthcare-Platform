# Database Schema Documentation

The system uses a unified SQLite relational database stored at `data/healthcare.db` to handle persistence.

## Database Tables

### 1. `users`
Tracks patient, doctor, and administrator credentials.
* `email` (TEXT, PRIMARY KEY): Unique identifier.
* `password` (TEXT): PBKDF2/SHA-256 hashed password.
* `role` (TEXT): Access control role (`Patient`, `Doctor`, `Admin`).
* `name` (TEXT): Full name of the user.
* `age` (INTEGER): User age.
* `gender` (TEXT): User gender.
* `blood_group` (TEXT): Blood group.
* `weight_kg` (REAL): Patient weight.
* `height_cm` (REAL): Patient height.
* `smoking` (TEXT): Smoking status.
* `alcohol` (TEXT): Alcohol consumption frequency.
* `family_history` (TEXT): Log of ancestral diseases.
* `prev_diseases` (TEXT): Existing clinical diagnoses.

### 2. `predictions`
Logs screening histories for all modules.
* `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
* `patient_email` (TEXT): Foreign key referencing `users(email)`.
* `disease` (TEXT): Screened module (`Diabetes`, `Heart Disease`, `Kidney Disease`, `Readmission`).
* `prediction` (INTEGER): Binary model output (`0` or `1`).
* `risk` (REAL): Risk probability output from model (`0.0` to `1.0`).
* `inputs_json` (TEXT): JSON dump of form fields utilized in the prediction.
* `timestamp` (TEXT): Date and time of screening.

### 3. `favorites`
Stores patient-saved clinics.
* `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
* `patient_email` (TEXT): Reference to `users(email)`.
* `clinic_name` (TEXT): Name of the facility.
* `clinic_address` (TEXT): Readable street address.
* `clinic_lat` (REAL): Coordinates (latitude).
* `clinic_lng` (REAL): Coordinates (longitude).
* `added_at` (TEXT): Timestamp when favorited.

### 4. `clinics_cache`
Caches geolocated facilities to reduce external Overpass API requests.
* `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
* `city_query` (TEXT): Composite cache key (`{city}_{disease}_{radius}`).
* `latitude` (REAL): Geocoded city latitude.
* `longitude` (REAL): Geocoded city longitude.
* `radius_km` (INTEGER): Search radius.
* `results_json` (TEXT): JSON array of returned facility objects.
* `fetched_at` (TEXT): Date of fetch. Caches are invalidated after 24 hours.

### 5. `followups`
Manages medication schedules, exercises, and consultations.
* `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
* `patient_email` (TEXT)
* `disease` (TEXT)
* `due_date` (TEXT): Scheduled date.
* `reminder_type` (TEXT): Category (`medicine`, `exercise`, `water`, `test`, `consultation`).
* `message` (TEXT): Text to display in reminders.
* `status` (TEXT): Reminder status (`pending` or `done`).
* `created_at` (TEXT): Creation date.

### 6. `appointments`
Logs appointment requests.
* `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
* `patient_email` (TEXT)
* `doctor_name` (TEXT): Name of doctor.
* `date_time` (TEXT): Scheduled date-time.
* `reason` (TEXT): Clinical reason.
* `status` (TEXT): Appointment state (`Scheduled`, `Cancelled`, `Completed`).
* `hospital_name` (TEXT): Hospital requested.
* `hospital_address` (TEXT): Address.
* `specialty` (TEXT): Medical field.
* `appointment_type` (TEXT): Mode (`request` or standard).

### 7. `doctor_notes`
Clinical notes entered by consulting doctors.
* `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
* `patient_email` (TEXT)
* `doctor_name` (TEXT)
* `note` (TEXT)
* `timestamp` (TEXT)

### 8. `audit_logs`
System activity tracker.
* `id` (INTEGER, PRIMARY KEY AUTOINCREMENT)
* `user_email` (TEXT)
* `action` (TEXT): Activity (`USER_LOGIN`, `PASSWORD_CHANGE`, `SCREENING_RUN`, etc.).
* `timestamp` (TEXT)
* `details` (TEXT)
