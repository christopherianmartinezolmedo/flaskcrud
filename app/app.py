import os
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

# Application initializations
app = Flask(__name__)

# settings
app.secret_key = os.getenv("SECRET_KEY", "dev-only-change-me")

# CSRF protection for every POST form
csrf = CSRFProtect(app)
