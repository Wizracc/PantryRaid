"""
pantry_raid/models/user.py
"""
import calendar
from mock import Mock, patch
from pantry_raid.models.user import User
from pytest import mark, raises
import time
from pantry_raid.models.user import User
from werkzeug.exceptions import Unauthorized
pytestmark = mark.unit


def test_init(app):
    """Need to test the functions it calls since they just set attributes."""
    form = Mock()
    form.username.data = "user"
    form.password.data = "password"
    form.email.data = "email"
    result = User(form=form, register=True)
    assert result.username == form.username.data
    assert result.email == form.email.data
    assert result.password != form.username.data

    # User doesn't exist
    with raises(Unauthorized):
        result = User(form=form, register=False)

    # Bad password
    form.username.data = "test"
    with raises(Unauthorized):
        result = User(form=form, register=False)

    # Good password
    form.password.data = "test"
    result = User(form=form, register=False)
    assert result.username == form.password.data

    # Too many bad passwords
    app.db.users.update_user_field(form.username.data, "set", "bad_logins", 5)
    app.db.users.update_user_field(form.username.data, "set", "last_bad_login", calendar.timegm(time.gmtime()))
    form.password.data = "bad"
    with raises(Unauthorized):
        result = User(form=form, register=False)

    deb = {
        "_id": "dude",
        "password": "where's my car",
        "email": "what."
    }
    result = User(doc=deb)
    assert result.database == deb
    assert result.username == deb["_id"]
    assert result.password == deb["password"]
    assert result.email == deb["email"]

    with raises(ValueError):
        User()


def test_get_id(app):
    form = Mock()
    form.username.data = "test"
    form.password.data = "test"
    u = User(form=form, register=False)
    assert u.get_id() == form.username.data


def test_save(app):
    form = Mock()
    form.username.data = "monkey"
    form.password.data = "monkey"
    form.email.data = "monkey@banana.kong"
    u = User(form=form, register=True)
    with raises(AttributeError):
        _ = u.database
    u.save()
    assert u.database is not None


def test_validate_login(app):
    u = app.db.users.find_by_username("test")
    passwd = "test"
    assert User.validate_login(u["password"], passwd)
