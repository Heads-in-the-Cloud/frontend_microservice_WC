from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.fields.core import DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):

    given_name = StringField('First Name',
                           validators=[DataRequired(), Length(min=2, max=20)])
    family_name = StringField('Last Name',
                           validators=[DataRequired(), Length(min=2, max=20)])

    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    phone = StringField('Phone',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')


class LoginForm(FlaskForm):
    username = StringField('Username',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class BookingGuestForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired()])
    phone = StringField('Phone', validators=[DataRequired()])
    submit = SubmitField('Continue to Booking')

class PassengerForm(FlaskForm):
    given_name = StringField('Given Name',
                        validators=[DataRequired()])
    family_name = StringField('Family Name', validators=[DataRequired()])
    dob = StringField('Date of Birth', validators=[DataRequired()])
    gender = StringField('Gender', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    submit = SubmitField('Book')

class UpdateUserForm(FlaskForm):
    username = StringField('Username')  
    given_name = StringField('Given Name')  
    family_name = StringField('Family Name')  
    email = StringField('Email')  
    password = StringField('Password')  
    phone = StringField('Phone')
    submit = SubmitField('Confirm')



