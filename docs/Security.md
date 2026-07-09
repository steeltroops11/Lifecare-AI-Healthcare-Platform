# Security & Hardening Policy

This document details the security safeguards built into the system.

## 🛡️ Hashing and Credentials
- **Password Storage**: Passwords are hashed using the standard PBKDF2 algorithm with a SHA-256 digest (`pbkdf2:sha256`) via Werkzeug's `generate_password_hash` and verified with `check_password_hash`. Plaintext credentials are never saved.
- **SQL Injection Prevention**: All database inputs are handled via parameterized queries (`?` place-holders) in `utils/database.py`. No raw string formatting or SQL string concatenation is utilized.

## 🔌 API Protection & Rate Limiting
- **Centralized Exception Wrapping**: All API requests and database queries are guarded by a `@safe_execute` decorator inside `utils/logger.py` that catches all runtime issues, logs them with stacktrace details, and returns a safe default fallback.
- **Search Rate Limiter**: The geocoding and specialist finder query is limited to **10 requests/minute** per user. If a user exceeds this limit, they are blocked and shown cached results.
- **Circuit Breaker**: If OpenRouteService is unreachable or times out, the circuit breaker trips and **deactivates the API for 5 minutes**, routing all queries to the local straight-line velocity fallback.
- **Strict Timout**: OpenStreetMap (Nominatim and Overpass) and OpenRouteService requests have a strict connection timeout limit of **2.5 seconds** to prevent page hang.

## 📋 Audit Logging
- All user-triggered updates, screen predictions, profile saves, credentials changes, and logins write to `audit_logs` in the SQLite database to track system security events.
- Audit logs contain the user's email, action performed, timestamp, and details.
