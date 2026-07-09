# pyrefly: ignore [missing-import]
import pytest
import utils.database as db
from werkzeug.security import generate_password_hash

def test_user_creation_and_retrieval():
    # Test creating user
    email = "test_user@example.com"
    pwd_hash = generate_password_hash("testpwd123")
    res = db.create_user(email, pwd_hash, "Patient", "Test Patient")
    assert res is True
    
    # Retrieve user and verify details
    user = db.get_user(email)
    assert user is not None
    assert user["name"] == "Test Patient"
    assert user["role"] == "Patient"
    
    # Duplicate creation should return False
    res_dup = db.create_user(email, pwd_hash, "Patient", "Dup Name")
    assert res_dup is False

def test_favorites_operations():
    email = "fav_user@example.com"
    db.add_favorite(email, "Apollo Clinic", "Ludhiana", 30.9, 75.8)
    
    favs = db.get_favorites(email)
    assert len(favs) == 1
    assert favs[0]["clinic_name"] == "Apollo Clinic"
    
    # Remove favorite
    db.remove_favorite(email, "Apollo Clinic")
    favs_after = db.get_favorites(email)
    assert len(favs_after) == 0

def test_followup_reminder_operations():
    email = "rem_user@example.com"
    db.add_followup(email, "Diabetes", "2026-07-10", "medicine", "Take Metformin")
    
    reminders = db.get_followups(email, status="pending")
    assert len(reminders) == 1
    assert reminders[0]["message"] == "Take Metformin"
    
    # Mark as completed
    db.update_followup_status(reminders[0]["id"], "done")
    rem_done = db.get_followups(email, status="done")
    assert len(rem_done) == 1
    assert rem_done[0]["status"] == "done"
