from flask_login import login_user, login_required, logout_user, current_user
from flask import abort, Blueprint, flash, redirect, render_template, request, url_for
from flask import current_app as app
from pantry_raid.models.forms import LoginForm, RegisterForm
from pantry_raid.models.user import User
from urllib.parse import urlparse, urljoin


user_manager = Blueprint('user_manager', __name__, template_folder='templates')


def create_user(regform):
    """Create a new user document based on RegisterForm data.

    Parameters
    ----------
    regform : pantry_raid.models.forms.registerform.RegisterForm
        WTForms registration form

    Returns
    -------
    pantry_raid.models.user.User
        New user object used by Flask-Login
    """
    new_user = User(form=regform, register=True)
    new_user.save()
    return new_user


def is_safe_url(target):
    """Copied from https://web.archive.org/web/20190217035443/http://flask.pocoo.org/snippets/62/

    Ensures that a target URL is safe to redirect to, since they often come from the `next` keyword in a URL that a malicious user could change.

    Parameters
    ----------
    target : string
        URL to check

    Returns
    -------
    boolean
        True if URL is safe
    """
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ("http", "https") and ref_url.netloc == test_url.netloc


"""Routes (URL endpoints) associated with user creation/authentication here"""


@user_manager.app_errorhandler(401)
def unauthorized(err):
    """Handles HTTP 401 (unauthorized) errors."""
    return render_template('401.html', form=LoginForm()), 401  # pragma: no cover


@user_manager.route('/logout')
@login_required
def logout():
    """Route to log out the current user."""
    logout_user()
    return render_template('index.html', user=current_user)


@user_manager.route('/register')
def register():
    """Route to register page."""
    return render_template('register.html',
                            user=current_user,
                            form=RegisterForm())


@user_manager.route('/register', methods=['POST'])
def register_post():
    """Route to register page on form submission."""
    form = RegisterForm()

    if form.validate_on_submit():
        if not app.db.users.username_exists(form.username.data):
            new_user = create_user(form)
            login_user(new_user)
            flash(f"Registration of user {form.username.data} succeeded.", "success")

            return redirect(url_for('routes.pantry'))
        flash(f"Username {form.username.data} already exists. If this is your username, please use the <a href='/login'>login form</a> instead.", "danger")

    return render_template('register.html',
                            user=current_user,
                            form=form)


@user_manager.route('/login')
def login():
    """Route to login page."""
    return render_template('login.html',
                            user=current_user,
                            form=LoginForm())


@user_manager.route('/login', methods=['POST'])
def login_post():
    """Route to login page on form submission."""
    form = LoginForm()

    if form.validate_on_submit():
        user = User(form=form, register=False)
        login_user(user)

        target_page = request.args.get('next')

        # Possible malicious redirect
        if not is_safe_url(target_page):
            abort(400)

        # Redirect after successful login
        return redirect(target_page or url_for('routes.search'))

    # Unable to validate, re-render the login form
    return render_template('login.html',
                            user=current_user,
                            form=form)
