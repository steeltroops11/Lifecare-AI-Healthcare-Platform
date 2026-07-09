from flask import Flask, render_template, request, redirect, url_for
from urllib.parse import quote
import json
import os
from dotenv import load_dotenv
from utils.logger import get_logger

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False  # Set to True only when serving over HTTPS in production

STREAMLIT_APP_URL = os.getenv("STREAMLIT_APP_URL", "http://localhost:8501")
USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")

logger = get_logger("login.auth_app")

from werkzeug.security import generate_password_hash, check_password_hash
import utils.database as db
from login.oauth import oauth

oauth.init_app(app)

# -----------------------------
# LOGIN ROUTE
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    error = request.args.get("error", "")
    selected_role = "Patient"

    if request.method == "POST":
        role = request.form.get("role", "Patient").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        selected_role = role
        
        # Load user from SQLite database (Priority 7)
        user = db.get_user(email)

        if not user:
            error = "No account found with this email."
            logger.warning(f"[LOCAL_LOGIN_FAIL] email='{email}' reason='no_account'")
            return render_template(
                "login.html",
                error=error,
                selected_role=selected_role
            )

        # Verify hashed password (Priority 7)
        if not check_password_hash(user["password"], password):
            error = "Incorrect password."
            logger.warning(f"[LOCAL_LOGIN_FAIL] email='{email}' reason='incorrect_password'")
            return render_template(
                "login.html",
                error=error,
                selected_role=selected_role
            )

        if user["role"].lower() != role.lower():
            error = f"This account is registered as {user['role']}, not {role}."
            logger.warning(f"[LOCAL_LOGIN_FAIL] email='{email}' reason='role_mismatch' expected='{user['role']}' actual='{role}'")
            return render_template(
                "login.html",
                error=error,
                selected_role=selected_role
            )

        # Log audit action
        db.add_audit_log(email, "USER_LOGIN", f"Role: {role} (Credentials Sign-in)")
        logger.info(f"[LOCAL_LOGIN_SUCCESS] email='{email}' role='{user['role']}'")

        redirect_url = (
            f"{STREAMLIT_APP_URL}/?"
            f"auth=1&role={quote(user['role'])}&email={quote(email)}&name={quote(user['name'])}"
        )
        return redirect(redirect_url)

    return render_template("login.html", error=error, selected_role=selected_role)


# -----------------------------
# SIGNUP ROUTE
# -----------------------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = ""
    success = ""

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not full_name or not email or not password or not confirm_password:
            error = "Please fill all fields."
            logger.warning(f"[SIGNUP_FAIL] email='{email}' reason='missing_fields'")
            return render_template("signup.html", error=error, success=success)

        # Check if user already exists in SQLite (Priority 7)
        if db.get_user(email):
            error = "An account with this email already exists."
            logger.warning(f"[SIGNUP_FAIL] email='{email}' reason='email_exists'")
            return render_template("signup.html", error=error, success=success)

        if password != confirm_password:
            error = "Passwords do not match."
            logger.warning(f"[SIGNUP_FAIL] email='{email}' reason='password_mismatch'")
            return render_template("signup.html", error=error, success=success)

        if len(password) < 6:
            error = "Password must be at least 6 characters long."
            logger.warning(f"[SIGNUP_FAIL] email='{email}' reason='password_too_short'")
            return render_template("signup.html", error=error, success=success)

        # Create user in SQLite database (Priority 7)
        created = db.create_user(email, password, "Patient", full_name)
        if created:
            success = "Account created successfully! You can now log in."
            logger.info(f"[SIGNUP_SUCCESS] email='{email}'")
        else:
            error = "An error occurred during account registration."
            logger.error(f"[SIGNUP_FAIL] email='{email}' reason='registration_error'")
            
        return render_template("signup.html", error=error, success=success)

    return render_template("signup.html", error=error, success=success)


# -----------------------------
# GOOGLE OAUTH LOGIN (Phase 2)
# -----------------------------
@app.route("/login/google")
def google_login_route():
    logger.info("[GOOGLE_OAUTH_INIT]")
    redirect_uri = request.host_url.rstrip('/') + '/auth/google/callback'
    return oauth.google.authorize_redirect(redirect_uri)


# -----------------------------
# GOOGLE OAUTH CALLBACK (Phase 3)
# -----------------------------
@app.route("/auth/google/callback")
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
    except Exception as e:
        logger.error(f"[GOOGLE_OAUTH_CALLBACK_FAIL] reason='token_failed' error='{str(e)}'")
        return redirect(url_for("login", error="Google Login Cancelled or failed to fetch access token."))

    userinfo = token.get('userinfo')
    if not userinfo:
        try:
            resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
            userinfo = resp.json()
        except Exception:
            pass

    if not userinfo:
        logger.error("[GOOGLE_OAUTH_CALLBACK_FAIL] reason='no_userinfo'")
        return redirect(url_for("login", error="Failed to retrieve Google user profile."))

    email = userinfo.get('email')
    email_verified = userinfo.get('email_verified')
    name = userinfo.get('name', 'Unknown User')

    if not email:
        logger.error("[GOOGLE_OAUTH_CALLBACK_FAIL] reason='no_email'")
        return redirect(url_for("login", error="Google Account has no email associated with it."))

    if not email_verified:
        logger.error(f"[GOOGLE_OAUTH_CALLBACK_FAIL] email='{email}' reason='email_unverified'")
        return redirect(url_for("login", error="Your Google email is not verified. Authentication rejected."))

    from utils.google_auth import find_or_create_google_user
    user = find_or_create_google_user(userinfo)

    if not user:
        logger.error(f"[GOOGLE_OAUTH_CALLBACK_FAIL] email='{email}' reason='sync_failed'")
        return redirect(url_for("login", error="Could not log in or register Google user account."))

    from flask import session
    session["logged_in"] = True
    session["email"] = user["email"]
    session["role"] = user["role"]
    session["name"] = user["name"]

    db.add_audit_log(
        user["email"],
        "LOGIN_GOOGLE",
        f"Role: {user['role']} (Google OAuth Sign-in), IP: {request.remote_addr}"
    )
    logger.info(f"[GOOGLE_OAUTH_CALLBACK_SUCCESS] email='{user['email']}' role='{user['role']}'")

    redirect_url = (
        f"{STREAMLIT_APP_URL}/?"
        f"auth=1&role={quote(user['role'])}&email={quote(user['email'])}&name={quote(user['name'])}"
    )
    return redirect(redirect_url)


# -----------------------------
# GOOGLE LOGIN SIMULATION (Priority 8)
# -----------------------------
@app.route("/google-login")
def google_login():
    # Return a clean page allowing user to select which mock Google account to log in with
    logger.info("[MOCK_GOOGLE_LOGIN_PAGE_ACCESSED]")
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Google Accounts - Sign In</title>
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Poppins', sans-serif;
                background: #f0f4f8;
                margin: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                color: #1a202c;
            }
            .container {
                background: white;
                border-radius: 16px;
                padding: 40px;
                box-shadow: 0 10px 25px rgba(0,0,0,0.05);
                width: 100%;
                max-width: 440px;
                text-align: center;
            }
            .logo {
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 24px;
            }
            .logo span:nth-child(1) { color: #4285F4; }
            .logo span:nth-child(2) { color: #EA4335; }
            .logo span:nth-child(3) { color: #FBBC05; }
            .logo span:nth-child(4) { color: #34A853; }
            h2 {
                font-size: 22px;
                margin-bottom: 8px;
                color: #2d3748;
            }
            p {
                color: #718096;
                font-size: 14px;
                margin-bottom: 30px;
            }
            .account-btn {
                display: flex;
                align-items: center;
                gap: 16px;
                width: 100%;
                padding: 16px;
                border: 1px solid #e2e8f0;
                border-radius: 12px;
                background: transparent;
                cursor: pointer;
                transition: all 0.2s;
                text-align: left;
                margin-bottom: 12px;
            }
            .account-btn:hover {
                background: #f7fafc;
                border-color: #cbd5e0;
                transform: translateY(-2px);
            }
            .avatar {
                width: 40px;
                height: 40px;
                border-radius: 50%;
                background: #ebf8ff;
                color: #2b6cb0;
                font-size: 20px;
                font-weight: bold;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .info {
                flex-grow: 1;
            }
            .info h4 {
                margin: 0;
                font-size: 15px;
                color: #2d3748;
            }
            .info p {
                margin: 2px 0 0;
                font-size: 12px;
                color: #718096;
            }
            .badge {
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 999px;
                font-weight: 700;
            }
            .badge-doc { background: #e6fffa; color: #319795; }
            .badge-pat { background: #ebf8ff; color: #2b6cb0; }
            .badge-adm { background: #fef2f2; color: #991b1b; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <span>G</span><span>o</span><span>o</span><span>g</span><span>l</span><span>e</span>
            </div>
            <h2>Choose an account</h2>
            <p>to continue to Healthcare Analytics</p>
            
            <button onclick="selectGoogleAccount('dr.navish.google@gmail.com', 'Doctor', 'Dr. Navish')" class="account-btn">
                <div class="avatar">N</div>
                <div class="info">
                    <h4>Dr. Navish</h4>
                    <p>dr.navish.google@gmail.com</p>
                </div>
                <span class="badge badge-doc">Doctor</span>
            </button>
            
            <button onclick="selectGoogleAccount('patient.google@gmail.com', 'Patient', 'John Doe')" class="account-btn">
                <div class="avatar">J</div>
                <div class="info">
                    <h4>John Doe</h4>
                    <p>patient.google@gmail.com</p>
                </div>
                <span class="badge badge-pat">Patient</span>
            </button>

            <button onclick="selectGoogleAccount('admin.google@gmail.com', 'Admin', 'System Admin')" class="account-btn">
                <div class="avatar">A</div>
                <div class="info">
                    <h4>System Admin</h4>
                    <p>admin.google@gmail.com</p>
                </div>
                <span class="badge badge-adm">Admin</span>
            </button>
        </div>
        
        <script>
            function selectGoogleAccount(email, role, name) {
                const redirectUrl = `/google-login/callback?role=${encodeURIComponent(role)}&email=${encodeURIComponent(email)}&name=${encodeURIComponent(name)}`;
                window.location.href = redirectUrl;
            }
        </script>
    </body>
    </html>
    """


@app.route("/google-login/callback")
def google_login_callback():
    email = request.args.get("email", "").strip().lower()
    role = request.args.get("role", "Patient").strip()
    name = request.args.get("name", "Google User").strip()
    
    logger.info(f"[MOCK_GOOGLE_LOGIN] email='{email}' role='{role}'")
    
    redirect_url = (
        f"{STREAMLIT_APP_URL}/?"
        f"auth=1&role={quote(role)}&email={quote(email)}&name={quote(name)}"
    )
    return redirect(redirect_url)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)