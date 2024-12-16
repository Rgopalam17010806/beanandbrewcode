from flask_login import UserMixin
from sqlalchemy import Nullable

from website import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=True)  # Nullable for Google sign-in users
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(15), nullable=True)
    role = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)

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
    day = db.Column(db.String(100), nullable = False)
    start_time = db.Column(db.Integer, nullable=False)
    end_time = db.Column(db.Integer, nullable=False)
    type_of_item = db.Column(db.String(50), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='onlinelessons', lazy = True)

class OnlineBakingLessonBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    course_name = db.Column(db.String(100), nullable=False)
    timing = db.Column(db.String(50), nullable=False)