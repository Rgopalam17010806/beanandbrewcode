import os

import bcrypt
from click import echo
from flask import Flask, render_template
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
import sqlalchemy as sa

db = SQLAlchemy()
mail = Mail()

DB_NAME = "database.db"

def send_email(subject, to, body):
    msg = Message(
                subject=subject, 
                sender='ritugopalam6@gmail.com',  # Ensure this matches MAIL_USERNAME
                recipients=[to]  # Replace with actual recipient's email
            )
    msg.body = body
    mail.send(msg)

def send_template_email(subject, to, template):
     msg = Message(
                 subject=subject, 
                 sender='ritugopalam6@gmail.com',  # Ensure this matches MAIL_USERNAME
                 recipients=[to]  # Replace with actual recipient's email
             )
     msg.html = render_template(template, user=current_user)
     mail.send(msg)


def create_app():
    app = Flask(__name__)
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    # Use your generated App Password
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'ritugopalam6@gmail.com'  # Use your actual Gmail address
    app.config['MAIL_PASSWORD'] = os.environ.get('GMAIL_APP_PASSWORD', None)
    mail=Mail(app)
    app.config['SECRET_KEY'] = 'my_secret_key'
    if os.getenv('DATABASE_URL'):
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace("postgres://", "postgresql://", 1)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)
    from .views import views
    from .auth import auth
    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    from .dbmodels import User
    register_cli_commands(app)
    engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    inspector = sa.inspect(engine)
    if not inspector.has_table("users"):
        with app.app_context():
            db.drop_all()
            db.create_all()
            app.logger.info('Initialized the database!')
    else:
        app.logger.info('Database already contains the users table.')
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


def register_cli_commands(app):
    @app.cli.command('init_db')
    def initialize_database():
        """Initialize the database."""
        db.drop_all()
        db.create_all()
        echo('Initialized the database!')