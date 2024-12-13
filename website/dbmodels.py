from flask_login import UserMixin

from website import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(150), nullable=False)
    lastname = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=True)
    role = db.Column(db.String(50), nullable=False)  # Add 'role' field
    basket_items = db.relationship('BasketItem', backref='user', lazy=True, cascade="all, delete-orphan")

class BasketItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # ForeignKey to User model


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



class OnlineLesson(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    firstname = db.Column(db.String(50),nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    nameoffoodordrink = db.Column(db.String(100), nullable=False)
    hours = db.Column(db.Integer, nullable=False)
    minutes = db.Column(db.Integer, nullable=False)
    type_of_item = db.Column(db.String(50), nullable=False)

class OnlineBakingLessonBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    timing = db.Column(db.String(50), nullable=False)