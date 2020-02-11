from flask_wtf import FlaskForm as Form
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, Length


class LoginForm(Form):
    username = StringField("Username", validators=[InputRequired("Username is required to login."), Length(min=2, max=32)])

    password = PasswordField("Password", validators=[InputRequired("Password must be between 4 and 32 characters."), Length(min=4, max=32)])

    submit = SubmitField("Login")
