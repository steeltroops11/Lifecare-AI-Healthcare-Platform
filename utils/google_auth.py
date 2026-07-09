import secrets
from datetime import datetime
from werkzeug.security import generate_password_hash
import utils.database as db
from utils.logger import get_logger

logger = get_logger("utils.google_auth")

def get_google_user(google_id):
    """Find a user in the database by their google_id."""
    conn = db.get_connection()
    row = conn.execute("SELECT * FROM users WHERE google_id = ?", (google_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

def update_last_login(email):
    """Update the last_login timestamp for the user."""
    conn = db.get_connection()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn.execute("UPDATE users SET last_login = ? WHERE email = ?", (now_str, email))
    conn.commit()
    conn.close()

def find_or_create_google_user(profile_info):
    """
    Find an existing user (by google_id or email) or automatically create a new Patient account.
    Returns the user record as a dictionary.
    """
    google_id = profile_info.get('sub')
    email = profile_info.get('email')
    name = profile_info.get('name', 'Google User')
    picture = profile_info.get('picture', '')
    email_verified = 1 if profile_info.get('email_verified') else 0
    
    # 1. Search by google_id
    user = get_google_user(google_id)
    if user:
        # Update last login and profile picture on every login
        conn = db.get_connection()
        conn.execute("""
            UPDATE users 
            SET profile_picture = ?
            WHERE google_id = ?
        """, (picture, google_id))
        conn.commit()
        conn.close()
        update_last_login(email)
        logger.info(f"[GOOGLE_USER_SYNC] email='{email}' action='found'")
        return get_google_user(google_id)
        
    # 2. If not found by google_id, check by email
    conn = db.get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    
    if row:
        # Existing local user: Link Google account to this user
        conn.execute("""
            UPDATE users 
            SET google_id = ?, profile_picture = ?, auth_provider = 'google', email_verified = ?
            WHERE email = ?
        """, (google_id, picture, email_verified, email))
        conn.commit()
        conn.close()
        update_last_login(email)
        logger.info(f"[GOOGLE_USER_SYNC] email='{email}' action='updated'")
        return get_google_user(google_id)
        
    # 3. User does not exist: Create a new Patient account (Option A)
    # Generate patient_id format (e.g. P-NAME)
    clean_name = "".join(c for c in name if c.isalnum()).upper()
    patient_id = f"P-{clean_name[:10]}"
    
    # Generate random password hash (no direct password access for OAuth users)
    dummy_password = generate_password_hash(secrets.token_hex(16))
    
    conn = db.get_connection()
    conn.execute("""
        INSERT INTO users (
            email, password, role, name, patient_id, 
            google_id, profile_picture, auth_provider, email_verified
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        email, dummy_password, 'Patient', name, patient_id,
        google_id, picture, 'google', email_verified
    ))
    conn.commit()
    conn.close()
    
    update_last_login(email)
    logger.info(f"[GOOGLE_USER_SYNC] email='{email}' action='created'")
    return get_google_user(google_id)
