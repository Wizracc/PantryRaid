from flask_wtf import FlaskForm as Form
from wtforms import PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired, Email, EqualTo, Length, Optional


class RegisterForm(Form):
    username = StringField("Username", validators=[InputRequired("Username is required for registration."), Length(min=2, max=32)])

    email = EmailField("E-mail (optional)", validators=[Email(message="Invalid e-mail address."), Optional()])

    password = PasswordField("Password", validators=[InputRequired("Password must be between 4 and 32 characters."), Length(min=4, max=32)])

    confirm_password = PasswordField("Repeat Password", validators=[InputRequired(), Length(min=4, max=32), EqualTo("password", message="Passwords must match.")])

    submit = SubmitField("Register")
