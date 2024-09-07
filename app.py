import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, Email
from flask_bcrypt import Bcrypt
from datetime import date
from functools import wraps 
from flask import abort

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
    firstname = db.Column(db.String(20), nullable=False)
    lastname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(10),nullable=False,default='user')


class TableBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(50), nullable=False)
    members = db.Column(db.Integer, nullable=False)
    timings = db.Column(db.String(50), nullable=False)
    dateofreservation = db.Column(db.Date, nullable=False)
    anyrequests = db.Column(db.String(200), nullable=True)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)

class RegisterForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    dateofbirth = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    role = SelectField('Role',choices=[('user','User'),('staff','Staff'),('manager','Manager')],default='user')
    submit = SubmitField('Register')

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError("That Email already exists. Please choose a different one.")

class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=60)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Remember Me')
    submit = SubmitField("Login")

class TableBooking(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    location = SelectField('Location', choices=[('Leeds', 'Leeds'), ('Harrowgate', 'Harrowgate'), ('Knaresborough castle', 'Knaresborough castle')])
    members = SelectField('Members', choices=[(str(i), str(i)) for i in range(1, 11)])
    timings = SelectField('Timings', choices=[('Morning (8:00 to 11:00)', 'Morning (8:00 to 11:00)'), ('Afternoon (11:00 to 17:00)', 'Afternoon (11:00 to 17:00)'), ('Evening (17:00 to 22:00)', 'Evening (17:00 to 22:00)')])
    dateofreservation = DateField('Date of Reservation', format='%Y-%m-%d', validators=[DataRequired()])
    anyrequests = StringField('Any Requests') 
    submit = SubmitField('Book Now')

    def validate_dateofreservation(self, dateofreservation):
        if dateofreservation.data < date.today():
            raise ValidationError('The reservation date cannot be in the past. Please choose a future date.')

class NewMenuItemForm(FlaskForm):
    name = StringField('Menu Item Name', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    price = StringField('Price', validators=[DataRequired()])
    category = SelectField('Category', choices=[('Drinks', 'Drinks'), ('Savory', 'Savory'), ('Sweet', 'Sweet')])
    submit = SubmitField('Add Menu Item')

class OnlineLessonTeacherForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    nameoffoodordrink = StringField('Name of Food or Drink', validators=[DataRequired()])
    

    hours = SelectField('Preferred Hour', choices=[(str(i), f'{i:02}') for i in range(24)], coerce=int)
    minutes = SelectField('Preferred Minute', choices=[(str(i), f'{i:02}') for i in range(0, 60, 5)], coerce=int)

    type_of_item = SelectField('Type of Item', choices=[
        ('drink', 'Drink'),
        ('sweet', 'Sweet'),
        ('savory', 'Savory')
    ])
    
    submit = SubmitField('Submit')


class OnlineLesson(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    firstname = db.Column(db.String(50),nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    nameoffoodordrink = db.Column(db.String(100), nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    type_of_item = db.Column(db.String(50), nullable=False)

class OnlineBakingLessonBookingForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    course_name = SelectField('Category', choices=[('How to bake Butter Croissants', 'How to bake Butter Croissants'), ('How to Bake Chocolate Cake', 'How to Chocolate Cake'), ('How to Bake Sourdough Bread', 'How to Bake Sourdough Bread')])





class OnlineBakingLessonBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    timing = db.Column(db.String(50), nullable=False)


@app.route('/addnewmenuitem', methods=['GET', 'POST'])
@login_required
def add_new_menu_item():
    if load_user(current_user.id).role != 'admin':
        flash('Sorry this is only for admins!', 'error')
        return redirect(url_for('home'))
    form = NewMenuItemForm()
    if form.validate_on_submit():
        # Clean the price input by removing currency symbols and commas
        price_str = form.price.data.strip().replace('£', '').replace(',', '')
        
        try:
            price = float(price_str)
        except ValueError:
            flash('Invalid price format. Please enter a numeric value.', 'danger')
            return redirect(url_for('add_new_menu_item'))

        new_item = MenuItem(
            name=form.name.data,
            description=form.description.data,
            price=price,
            category=form.category.data
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Menu item added successfully!', 'success')
        return redirect(url_for('add_new_menu_item'))
    return render_template('addnewmenuitem.html', form=form)


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
        user = User.query.filter_by(email=form.email.data).first()
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
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(firstname=form.firstname.data,
                        lastname=form.lastname.data,
                        email=form.email.data,
                        password=hashed_password,
                        role=form.role.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        flash('Registration successful! You are now logged in.', 'success')
        return redirect(url_for('home'))
    return render_template('register.html', form=form)

@login_required
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

@app.route('/tablebooking', methods=['GET', 'POST'])
def tablebooking():
    form = TableBooking()
    today_date = date.today().strftime('%Y-%m-%d')
    if form.validate_on_submit():
        new_booking = TableBooking(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            location=form.location.data,
            members=int(form.members.data),  # Convert members to int
            timings=form.timings.data,
            dateofreservation=form.dateofreservation.data,
            anyrequests=form.anyrequests.data
        )
        db.session.add(new_booking)
        db.session.commit()
        flash("Table is booked successfully!", "success")
        return redirect(url_for('home'))
    return render_template('tablebooking.html', form=form, today_date=today_date)

@app.route('/onlinelessonbooking', methods=['GET', 'POST'])
@login_required
def onlinelessonbooking():
    form = OnlineLessonTeacherForm()
    if form.validate_on_submit():
        new_lesson = OnlineLesson(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
            nameoffoodordrink=form.nameoffoodordrink.data,
            hours=form.hours.data,
            minutes=form.minutes.data,
            type_of_item=form.type_of_item.data
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash('Your online lesson booking has been submitted successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('onlinebakinglessons.html', form=form)

def load_menu():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "menu_items.json")
    with open(json_url) as menu_file:
        return json.load(menu_file)

@app.route('/drinks')
def drinks():
    menu = load_menu()
    return render_template('drinks.html', hot_drinks=menu['hot drinks'], cold_drinks=menu['cold drinks'])

@app.route('/savory')
def savory():
    menu = load_menu()
    return render_template('savory.html', sandwiches=menu['sandwiches'], salads=menu['salads'])

@app.route('/sweet')
def sweet():
    menu = load_menu()
    return render_template('sweet.html', pastries=menu['pastries'], cakes=menu['cakes'])

@app.route('/hampers')
def hampers():
    menu = load_menu()
    return render_template('hampers.html', hampers=menu['hampers'])

@app.route('/teachonlinebakinglessons', methods=['GET', 'POST'])
def teachonlinebakinglessons():
    form = OnlineLessonTeacherForm()
    if form.validate_on_submit():
        new_lesson = OnlineLesson(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
            nameoffoodordrink=form.nameoffoodordrink.data,
            hours=form.hours.data,
            minutes=form.minutes.data,
            type_of_item=form.type_of_item.data
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash('Your online lesson booking has been submitted!', 'success')
        return redirect(url_for('home'))
    return render_template('teachonlinebakinglessons.html', form=form)

@app.route('/add_to_basket', methods=['POST'])
def add_to_basket():
    item_name = request.form.get('item_name')
    item_price = float(request.form.get('item_price'))
    quantity = int(request.form.get('quantity'))
    # Initialize the session basket if it doesn't exist
    basket = session.get('basket', [])
    # Add the item to the session basket
    basket.append({
        'name': item_name,
        'price': item_price,
        'quantity': quantity
    })
    session["basket"] = basket
    # Redirect to the basket page after adding an item
    return redirect(url_for('your_basket'))

# Route to display the basket page
@app.route('/your_basket')
def your_basket():
    # Get the basket from the session, or use an empty list if it doesn't exist
    basket = session.get('basket', [])
    # Calculate the total price
    total_price = sum(item['price'] * item['quantity'] for item in basket)
    return render_template('basket.html', cart=basket, total_price=total_price)


@app.route('/clear_basket')
def clear_basket():
    session['basket'] = []
    return redirect(url_for('your_basket'))


@app.route('/proceed_to_payment', methods=['GET', 'POST'])
def proceed_to_payment():
    if request.method == 'POST':
        if current_user.is_authenticated:
            current_user.basket_items.clear()
            db.session.commit()
            
        session.pop('basket', None) 

        return redirect(url_for('yourorder'))

    return render_template('proceed_to_payment.html')


@app.route('/yourorder')
def yourorder():
    return render_template('yourorder.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)