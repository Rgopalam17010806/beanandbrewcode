from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, Email
from flask_bcrypt import Bcrypt
from flask_login import LoginManager,current_user
from flask_login import login_user
from flask_login import logout_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thissecretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(20),nullable=False)
    lastname = db.Column(db.String(20),nullable = False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    dateofbirth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("That Username already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=60)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Login")

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # Hash the user's password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Create a new user instance
        new_user = User(email=form.email.data,
                        username=form.username.data,
                        password=hashed_password)
        
        # Add the user to the database
        db.session.add(new_user)
        db.session.commit()
        
        # Log the user in automatically
        login_user(new_user)
        
        # Flash a success message
        flash('Registration successful! You are now logged in.', 'success')
        
        # Redirect to the home page or another page of your choice
        return redirect(url_for('home'))
    
    # Render the registration template if the form is not validated
    return render_template('register.html', form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('home'))


@app.route('/aboutus')
def aboutus():
    return render_template('about_us.html')

@app.route('/menus')
def menus():
    return render_template('menus.html')

@app.route('/locations')
def locations():
    return render_template('locations.html')

@app.route('/tablebooking')
def tablebooking():
    return render_template('tablebooking.html')

@app.route('/onlinelessonbooking')
def onlinelessonbooking():
    return render_template('onlinebakinglessons.html')

@app.route('/drinks')
def drinks():
    return render_template('drinks.html')

@app.route('/savory')
def savory():
    return render_template('savory.html')

@app.route('/sweet')
def sweet():
    return render_template('sweet.html')

@app.route('/personalisedhampers')
def personalisedhampers():
    return render_template('personalisedhampers.html')

if __name__ == '__main__':
    app.run(debug=True)