import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

# Load .env variables
load_dotenv()

oauth = OAuth()

# Register Google OAuth Client
oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
