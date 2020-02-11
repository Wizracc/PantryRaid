"""
pantry_raid/models/usercollection.py
"""
from mock import Mock
from pantry_raid.models.status import Status
from pytest import mark, raises
pytestmark = mark.unit


def test_find_by_username(app):
    user = "test"
    result = app.db.users.find_by_username(user)
    assert result is not None
    assert result['_id'] == "test"
    assert result['email'] == "test@email.cx"


def test_username_exists(app):
    user = "test"
    assert app.db.users.username_exists(user) is True


def test_add_new_user(app):
    user = Mock()
    user.username = "monkey"
    user.password = "password"
    user.email = "email@mail.not"
    result = app.db.users.add_new_user(user)
    assert result.acknowledged is True
    assert result.inserted_id == user.username


def test_update_user_field(app):
    user = "test"
    operation = "push"
    field = "pantry"
    value = "test item"
    result = app.db.users.update_user_field(user, operation, field, value)
    assert result.matched_count == 1
    assert result.modified_count == 1


def test_increment_bad_logins(app):
    user = "test"
    time = 64
    app.db.users.increment_bad_logins(user, time)
    doc = app.db.users.find_by_username(user)
    assert doc['bad_logins'] == 1
    assert doc['last_bad_login'] == time


def test_reset_bad_logins(app):
    user = "test"
    time = 64
    app.db.users.increment_bad_logins(user, time)
    doc = app.db.users.find_by_username(user)
    assert doc['bad_logins'] == 1
    assert doc['last_bad_login'] == time
    app.db.users.reset_bad_logins(user)
    doc = app.db.users.find_by_username(user)
    assert doc['bad_logins'] == 0
    assert doc['last_bad_login'] == 0


def test_pantry_insert_ingredient(app):
    user = "test"
    ing = "dracula"
    result = app.db.users.pantry_insert_ingredient(ing, user)
    assert result == Status("success", f"Added {ing} to your pantry.")


def test_pantry_remove_ingredient(app):
    user = "test"
    ing = "dracula"
    result = app.db.users.pantry_remove_ingredient(ing, user)
    assert result == Status("info", f"Removed {ing} from your pantry.")


def test_favorites_insert_recipe(app, test_login):
    """Update this test when implemented"""
    user = "test"
    recipe = "test recipe"
    orig = app.db.get_favorites()
    app.db.users.favorites_insert_recipe(recipe, user)
    new = app.db.get_favorites()
    assert sorted(orig) != sorted(new)


def test_substitute_insert(app):
    substitution = {
        "name": "sample",
        "quantity": "one bazillion",
        "items": [
                {
                    "ingredient": "nothing",
                    "quantity": "all"
                }
        ]
    }
    user = "test"
    old_subs = app.db.users.find_by_username(user).get('substitutes')
    resp = app.db.users.substitute_insert(substitution, user)
    assert resp.css == Status("success", "test").css
    subs = app.db.users.find_by_username(user).get('substitutes')
    assert subs != old_subs


def test_substitute_remove(app):
    idx = '5'
    user = "test"
    resp = app.db.users.substitute_remove(idx, user)
    assert resp.css == Status("info", "test").css


def test_get_pantry_with_substitutions(app):
    user = "test"
    substitution = {
        "name": "sample",
        "quantity": "one bazillion",
        "items": [
                {
                    "ingredient": "cream cheese",
                    "quantity": "all"
                }
        ]
    }
    sub2 = {
        "name": "dead rat",
        "quantity": "one bazillion",
        "items": [
                {
                    "ingredient": "nothing",
                    "quantity": "all"
                }
        ]
    }
    user = "test"
    # simulate adding some sub since the test user probably has none
    app.db.users.substitute_insert(substitution, user)
    app.db.users.substitute_insert(sub2, user)
    resp = app.db.users.get_pantry_with_substitutions(user)
    assert substitution.get('name') in resp
    assert sub2.get('name') not in resp
