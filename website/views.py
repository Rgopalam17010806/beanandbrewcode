from datetime import date
import json
import os
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import login_required, current_user, login_user, logout_user
from flask_mail import Message
from website import db, send_email, send_template_email
from website.dbmodels import BasketItem, MenuItem, OnlineLesson, TableBooking, User
from website.formmodels import LoginForm, NewMenuItemForm, OnlineLessonTeacherForm, RegisterForm, TableBookingForm

views = Blueprint('views', __name__)


@views.route('/addnewmenuitem', methods=['GET', 'POST'])
@login_required
def add_new_menu_item():
    if current_user.role != 'ADMIN':
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
        return redirect(url_for('views.add_new_menu_item'))
    return render_template('addnewmenuitem.html', form=form)


@views.route('/home')
def home():
    return render_template('home.html')


@views.route('/')
def index():
    return render_template("home.html")


@views.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Login successful!', 'success')
            return redirect(url_for('views.home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


@views.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        #hash the password 
        hashed_password = generate_password_hash(form.password.data)

        #create a new user instance
        new_user = User(first_name=form.firstname.data,
                        last_name=form.lastname.data,
                        email=form.email.data,
                        password=hashed_password,
                        role=form.role.data,
                        type = "CUSTOM"
        )

        #add user to the database
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, False)
        flash('Registration successful! You are now logged in.', 'success')
        return redirect(url_for('views.home'))
    
    return render_template('register.html', form=form)


@views.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', username=session['username'])
    return redirect(url_for('views.home'))


@login_required
@views.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('views.home'))


@views.route('/aboutus')
def aboutus():
    return render_template('about_us.html')


@views.route('/menus')
def menus():
    return render_template('menus.html')


@views.route('/locations')
def locations():
    return render_template('locations.html')


@views.route('/tablebooking', methods=['GET', 'POST'])
def tablebooking():
    form = TableBookingForm()
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


@views.route('/onlinelessonbooking', methods=['GET', 'POST'])
@login_required
def onlinelessonbooking():
    onlinelessons = OnlineLesson.query.filter_by(user_id=current_user.id).all()
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
    return render_template('onlinebakinglessons.html', form=form, onlinelessons = onlinelessons)


def load_menu():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "menu_items.json")
    with open(json_url) as menu_file:
        return json.load(menu_file)
    
@views.route('/viewlessons')
@login_required
def viewlessons():
    #fetch the lessons associated with the currently logged in user
    lessons =OnlineLesson.query.filter_by(user_id=current_user.id).all()

    # if no lessons are booked, show a message 
    if not lessons:
        flash('You have not booked any lessons let!', 'info')

    return render_template('viewlessons.html', lessons=lessons)


@views.route('/drinks')
def drinks():
    menu = load_menu()
    return render_template('drinks.html', hot_drinks=menu['hot drinks'], cold_drinks=menu['cold drinks'])


@views.route('/savory')
def savory():
    menu = load_menu()
    return render_template('savory.html', sandwiches=menu['sandwiches'], salads=menu['salads'])


@views.route('/sweet')
def sweet():
    menu = load_menu()
    return render_template('sweet.html', pastries=menu['pastries'], cakes=menu['cakes'])


@views.route('/hampers')
def hampers():
    menu = load_menu()
    return render_template('hampers.html', hampers=menu['hampers'])


@views.route('/teachonlinebakinglessons', methods=['GET', 'POST'])
def teachonlinebakinglessons():
    form = OnlineLessonTeacherForm()
    if form.validate_on_submit():
        new_lesson = OnlineLesson(
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            email=form.email.data,
            nameoffoodordrink=form.nameoffoodordrink.data,
            day = form.day.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            type_of_item=form.type_of_item.data,
            user_id = current_user.id
        )
        db.session.add(new_lesson)
        db.session.commit()
        flash('Your online lesson booking has been submitted!', 'success')
        return redirect(url_for('views.home'))
    return render_template('teachonlinebakinglessons.html', form=form)


@views.route('/add_to_basket', methods=['POST'])
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
    return redirect(url_for('views.your_basket'))


# Route to display the basket page
@views.route('/your_basket')
def your_basket():
    # Get the basket from the session, or use an empty list if it doesn't exist
    basket = session.get('basket', [])
    # Calculate the total price
    total_price = sum(item['price'] * item['quantity'] for item in basket)
    return render_template('basket.html', cart=basket, total_price=total_price)


@views.route('/clear_basket')
def clear_basket():
    session['basket'] = []
    return redirect(url_for('your_basket'))


@views.route('/proceed_to_payment', methods=['GET', 'POST'])
@login_required
def proceed_to_payment():
    if request.method == 'POST':
        if current_user.is_authenticated:
            # Clear the user's basket items
            BasketItem.query.filter_by(user_id=current_user.id).delete()
            db.session.commit()
            # Clear the session basket (if you are storing it in the session)
            session.pop('basket', None)
            # email = current_user.email
            # send_email(subject="Thank you for your purchase",to=email,body="Your order has been confirmed and we hope you have enjoyed checking out our store.")
            send_template_email(subject="Thank you for your purchase",to=current_user.email,template="emails/purchase.html")
        return redirect(url_for('views.home'))
    return render_template('proceed_to_payment.html')
