import calendar
from flask_login import UserMixin
from flask import abort, flash
from flask import current_app as app
import time
from werkzeug.security import check_password_hash, generate_password_hash


class User(UserMixin):
    def __init__(self, **kwargs):
        """Volatile user class for Flask-Login. Not to be confused with the persistent database-related user (pantry_raid.models.usercollection.UserCollection).

        This class is only used for login, logout, and registration purposes. It does not maintain database interactivity. For the database-related functions, see UserCollection.

        Attributes
        ----------
        username : string

        password : string
            SHA-256 hashed password

        email : string

        Parameters
        ----------
        kwargs : keyword arguments, packed into a dict
            Should contain one of `form`, when the user sent information through a form, or `doc`, when the user navigates to any page. Flask-Login's login manager needs to check the user on every page.
        """
        if "form" in kwargs.keys():
            form = kwargs['form']
            self.username = form.username.data
            if kwargs['register']:
                self.setup_new_user(form)
            else:
                self.setup_returning_user(form)

        elif "doc" in kwargs.keys():
            self.for_logman(kwargs['doc'])

        else:
            raise ValueError("Unable to generate user object.")

    def for_logman(self, from_db):
        """Used for the login manager, since form data is not available.

        Parameters
        ----------
        from_db : pymongo.Document
            Document from the UserCollection corresponding to this user
        """
        self.database = from_db
        self.username = from_db["_id"]
        self.password = from_db["password"]
        self.email = from_db["email"]

    def setup_new_user(self, form):
        """
        Parameters
        ----------
        form : pantry_raid.models.forms.registerform.RegisterForm
        """
        self.password = generate_password_hash(form.password.data, method='sha256')
        self.email = form.email.data

    def setup_returning_user(self, form):
        """Sets up a returing user logging in by verifying the login information and getting the user document. If the user provides the wrong password five times, they are blocked from attempting to log in for 15 minutes. The same message is repeated any time a login failure occurs to prevent information leakage by intentionally obscuring the details of the failure.

        Parameters
        ----------
        form : pantry_raid.models.forms.loginform.LoginForm
        """
        bad_login_msg = "Username or password is incorrect. Please <a href='{{ url_for('user_manager.register')}}'>register</a> or try again. If you fail to enter the correct password five times within 15 minutes, your account will be locked for the next 15 minutes."
        user_obj = app.db.users.find_by_username(self.username)

        now = calendar.timegm(time.gmtime())

        if user_obj is None or user_obj['bad_logins'] >= 5 and now - user_obj['last_bad_login'] < 900:
            flash(bad_login_msg, "danger")
            abort(401)

        if not User.validate_login(user_obj['password'], form.password.data):
            flash(bad_login_msg, "danger")
            app.db.users.increment_bad_logins(self.username, now)
            abort(401)

        app.db.users.reset_bad_logins(self.username)
        self.database = user_obj

    def get_id(self):
        """Overridden UserMixin function to return the primary key of the user.

        Returns
        -------
        string
            Username
        """
        return self.username

    def save(self):
        """Add a new user to the database."""
        ack = app.db.users.add_new_user(self)
        self.database = app.db.users.find_by_username(ack.inserted_id)

    @staticmethod
    def validate_login(password_hash, password):
        """Verifies that the correct password for this user was submitted.

        Returns
        -------
        boolean
            True if password is correct
        """
        return check_password_hash(password_hash, password)
