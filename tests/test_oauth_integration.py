import pytest
import sqlite3
from flask import session
from urllib.parse import quote
from login.auth_app import app
from login.oauth import oauth
import utils.database as db
import utils.google_auth as google_auth

@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["SECRET_KEY"] = "test-secret-key-123"
    with app.test_client() as client:
        yield client

def test_google_auth_create_new_user():
    # Test automatically creating a Patient account for a new Google user
    profile_info = {
        "sub": "google-id-12345",
        "email": "newpatient@gmail.com",
        "name": "Jane Doe",
        "picture": "http://example.com/jane.jpg",
        "email_verified": True
    }
    
    # Assert database does not have this user initially
    assert db.get_user("newpatient@gmail.com") is None
    
    # Run creation helper
    user = google_auth.find_or_create_google_user(profile_info)
    
    assert user is not None
    assert user["email"] == "newpatient@gmail.com"
    assert user["role"] == "Patient"
    assert user["google_id"] == "google-id-12345"
    assert user["auth_provider"] == "google"
    assert user["profile_picture"] == "http://example.com/jane.jpg"
    assert user["email_verified"] == 1
    assert user["patient_id"].startswith("P-")

def test_google_auth_link_existing_user():
    # Pre-create a local user
    email = "existinguser@gmail.com"
    assert db.get_user(email) is None
    db.create_user(email, "localpassword123", "Doctor", "Dr. Local")
    
    profile_info = {
        "sub": "google-id-67890",
        "email": email,
        "name": "Dr. Local",
        "picture": "http://example.com/local.jpg",
        "email_verified": True
    }
    
    # Run linker helper
    user = google_auth.find_or_create_google_user(profile_info)
    
    assert user is not None
    # User retains Doctor role and name from initial creation
    assert user["email"] == email
    assert user["role"] == "Doctor"
    assert user["google_id"] == "google-id-67890"
    assert user["auth_provider"] == "google"
    assert user["profile_picture"] == "http://example.com/local.jpg"
    
    # Verify no duplicate user is created
    conn = db.get_connection()
    count = conn.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,)).fetchone()[0]
    conn.close()
    assert count == 1

def test_google_auth_update_profile_picture_on_login():
    profile_info = {
        "sub": "google-id-9999",
        "email": "picsync@gmail.com",
        "name": "Pic Sync User",
        "picture": "http://example.com/old.jpg",
        "email_verified": True
    }
    
    google_auth.find_or_create_google_user(profile_info)
    
    # Update picture
    profile_info["picture"] = "http://example.com/new.jpg"
    user = google_auth.find_or_create_google_user(profile_info)
    
    assert user["profile_picture"] == "http://example.com/new.jpg"

def test_local_login_works(client):
    # Test credential login on Flask app
    email = "locallogintest@gmail.com"
    db.create_user(email, "pass123", "Patient", "Local Login Tester")
    
    # Call endpoint with invalid password
    response = client.post("/", data={
        "role": "Patient",
        "email": email,
        "password": "wrongpassword"
    })
    assert b"Incorrect password." in response.data
    
    # Call endpoint with valid password
    response = client.post("/", data={
        "role": "Patient",
        "email": email,
        "password": "pass123"
    })
    assert response.status_code == 302
    assert "http://localhost:8501" in response.headers["Location"]
    assert "auth=1" in response.headers["Location"]
    
    # Verify audit logs contain local login
    logs = db.get_audit_logs()
    login_logs = [l for l in logs if l["action"] == "USER_LOGIN" and l["user_email"] == email]
    assert len(login_logs) == 1
    assert "Credentials Sign-in" in login_logs[0]["details"]

def test_google_login_redirect(client, monkeypatch):
    from flask import redirect
    monkeypatch.setattr(oauth.google, "authorize_redirect", lambda r: redirect("https://accounts.google.com/mock-auth"))
    
    response = client.get("/login/google")
    assert response.status_code == 302
    assert response.headers["Location"] == "https://accounts.google.com/mock-auth"

def test_google_callback_cancellation(client, monkeypatch):
    # Force exception during authorize_access_token to simulate cancellation/errors
    def mock_raise():
        raise Exception("OAuth error")
        
    monkeypatch.setattr(oauth.google, "authorize_access_token", mock_raise)
    
    response = client.get("/auth/google/callback")
    assert response.status_code == 302
    assert "/?error=" in response.headers["Location"]
    assert "Google+Login+Cancelled" in response.headers["Location"]

def test_google_callback_success(client, monkeypatch):
    mock_profile = {
        "sub": "google-success-id",
        "email": "googlesuccess@gmail.com",
        "name": "Google Success",
        "picture": "http://example.com/success.jpg",
        "email_verified": True
    }
    
    monkeypatch.setattr(oauth.google, "authorize_access_token", lambda: {"userinfo": mock_profile})
    
    response = client.get("/auth/google/callback")
    
    # 1. Assert redirection to Streamlit dashboard
    assert response.status_code == 302
    location = response.headers["Location"]
    assert "http://localhost:8501" in location
    assert "auth=1" in location
    assert "email=googlesuccess%40gmail.com" in location
    assert "role=Patient" in location
    
    # 2. Assert Flask session variables are populated correctly
    with client.session_transaction() as sess:
        assert sess["logged_in"] is True
        assert sess["email"] == "googlesuccess@gmail.com"
        assert sess["role"] == "Patient"
        assert sess["name"] == "Google Success"
        
    # 3. Assert user is created in database
    user = db.get_user("googlesuccess@gmail.com")
    assert user is not None
    assert user["google_id"] == "google-success-id"
    assert user["profile_picture"] == "http://example.com/success.jpg"
    assert user["auth_provider"] == "google"
    
    # 4. Assert audit log is written
    logs = db.get_audit_logs()
    google_logs = [l for l in logs if l["action"] == "LOGIN_GOOGLE" and l["user_email"] == "googlesuccess@gmail.com"]
    assert len(google_logs) == 1
    assert "Google OAuth Sign-in" in google_logs[0]["details"]
