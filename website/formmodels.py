from datetime import date
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField
from wtforms.validators import InputRequired, Length, ValidationError, DataRequired, Email

from website.dbmodels import User

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

class TableBookingForm(FlaskForm):
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


class OnlineBakingLessonBookingForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    course_name = SelectField('Category', choices=[('How to bake Butter Croissants', 'How to bake Butter Croissants'), ('How to Bake Chocolate Cake', 'How to Chocolate Cake'), ('How to Bake Sourdough Bread', 'How to Bake Sourdough Bread')])
