import json
import os
import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for
from oauthlib.oauth2 import WebApplicationClient
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, login_user, logout_user, current_user
from website import db
from website.dbmodels import User

auth = Blueprint('auth', __name__)

# Constants for Google OAuth
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET')

# OAuth client setup
client = WebApplicationClient(GOOGLE_CLIENT_ID)

def get_google_provider_config():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

@auth.route('/google', methods=['GET'])
def google():
    google_provider_config = get_google_provider_config()
    authorization_endpoint = google_provider_config['authorization_endpoint']
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.host_url + "callback",
        scope=["openid", "email", "profile"]
    )
    return redirect(request_uri)

@auth.route('/callback')
def callback():
    code = request.args.get('code')
    google_provider_config = get_google_provider_config()
    token_endpoint = google_provider_config['token_endpoint']

    # Exchange authorization code for a token
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )

    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET)
    )

    if token_response.status_code != 200:
        flash(f'Failed to obtain token: {token_response.text}', category='error')
        return redirect(url_for('auth.login'))

    client.parse_request_body_response(json.dumps(token_response.json()))

    # Retrieve user information
    userinfo_endpoint = google_provider_config['userinfo_endpoint']
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body).json()

    if userinfo_response.get('email_verified'):
        users_email = userinfo_response['email']
        first_name = userinfo_response['given_name']
        last_name = userinfo_response['family_name']

        # Find or create the user
        user = User.query.filter_by(email=users_email).first()
        if not user:
            user = User(
                email=users_email, 
                password='', 
                first_name=first_name,
                last_name=last_name, 
                phone='', 
                type='GOOGLE'
            )
            db.session.add(user)
            db.session.commit()

        if user.type != "GOOGLE":
            flash('You previously signed up using another method. Please use that method to log in.', category='error')
        else:
            login_user(user, remember=True)
            flash('Signed in successfully!', category='success')

        return redirect(url_for('views.home'))

    flash('Unable to log in. Please try again.', category='error')
    return redirect(url_for('auth.login'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if user:
            if user.type == "GOOGLE":
                flash('Please use Google sign-in.', category='error')
            elif check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash('Logged in successfully!', category='success')
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password.', category='error')
        else:
            flash('User does not exist.', category='error')

    return render_template("login.html", user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        email = request.form.get("email")
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        phone = request.form.get("phone")

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already registered. If you used Google sign-in, please use that to log in.', category='error')
        elif len(email) < 4:
            flash('Email must be at least 4 characters.', category='error')
        elif password != confirm:
            flash('Passwords do not match.', category='error')
        else:
            user = User(
                email=email,
                password=generate_password_hash(password, method='sha256'),
                first_name=firstName,
                last_name=lastName,
                phone=phone,
                type='CUSTOM'
            )
            db.session.add(user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account created successfully!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)
