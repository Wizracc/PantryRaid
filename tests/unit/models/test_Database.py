"""
pantry_raid/models/database.py

The `app` fixture patches the `setup_mongoclient` function, so don't use it if you need to test that function.
"""
from flask import url_for
from pantry_raid.config import TestConfig
from pantry_raid.models.database import Database
from pantry_raid.models.recipes import Recipes
from pantry_raid.models.ingredients import Ingredients
from pantry_raid.models.pantry import Pantry
from pantry_raid.models.status import Status
from pytest import mark
pytestmark = mark.unit


"""The application factory handles converting the config from an object into something usable by Flask. Tests fail when you just run the raw config object into the database due to type differences.
"""
testconf = {
    "TESTING": TestConfig.TESTING,
    "CONNECTION_URL": TestConfig.CONNECTION_URL
}
db = Database(testconf)


def test_init():
    assert db.config['TESTING'] is TestConfig.TESTING
    assert db.config['CONNECTION_URL'] == TestConfig.CONNECTION_URL
    assert type(db.recipes) is Recipes
    assert type(db.ingredients) is Ingredients
    assert type(db.pantry) is Pantry


def test_setup_mongoclient():
    stat = db.setup_mongoclient()
    assert stat.HOST == db.mongoc.HOST


def test_get_all_ingredients(app):
    db_ings = app.db.get_all_ingredients()
    ing_ings = app.db.ingredients.get_as_list()
    assert db_ings == ing_ings


def test_get_all_recipes(app):
    db_rec = app.db.get_all_recipes()
    rec_rec = app.db.recipes.get_as_list()
    assert db_rec == rec_rec


def test_get_pantry_contents(app):
    db_pantry = app.db.get_pantry_contents()
    pant_pantry = app.db.pantry.get_as_list()
    assert db_pantry == sorted(pant_pantry, key=lambda v: v.upper())


def test_add_ingredient_to_pantry(app):
    bad = "MOCK_PANTRY"
    bad_ret = app.db.add_ingredient_to_pantry(bad)
    assert bad_ret == Status("danger", f"Error: '{bad}' is not a valid ingredient")

    already = "butter"
    already_ret = app.db.add_ingredient_to_pantry(already)
    assert already_ret == Status("danger", f"Error: '{already}' is already in your pantry.")

    good = "quinoa"
    good_ret = app.db.add_ingredient_to_pantry(good)
    assert good_ret == Status("success", f"Added {good} to your pantry.")


def test_get_recipe_by_id(app):
    rid = "20876"
    db_get = app.db.get_recipe_by_id(rid)
    rec_get = app.db.recipes.get_by_id(rid)
    assert db_get == rec_get


def test_user_get_contents(app, test_login, client):
    # Check the logged in user's pantry
    user_pantry = app.db.get_pantry_contents()
    # Logout
    client.get(url_for('user_manager.logout'))
    # Check the anonymous user's pantry
    anon = app.db.get_pantry_contents()
    assert sorted(user_pantry) != sorted(anon)


def test_user_add_ingredient(app, test_login):
    food = "bacon"
    resp = app.db.add_ingredient_to_pantry(food)
    assert resp.css == "has-text-success"


def test_user_remove_ingredient(app, test_login):
    food = "butter"
    resp = app.db.remove_ingredient_from_pantry(food)
    assert resp.css == "has-text-info"
    not_food = "deku nut"
    resp = app.db.remove_ingredient_from_pantry(not_food)
    assert resp.css == "has-text-danger"


def test_anonymous_remove_ingredient(app):
    food = "eggs"
    resp = app.db.remove_ingredient_from_pantry(food)
    assert resp.css == "has-text-info"


def test_get_substitutions(app, test_login):
    resp = app.db.get_substitutions()
    its = list(resp[0].items())
    assert ("name", "thing") == its[0]


def test_insert_substitution_anon(app):
    sub = {}
    resp = app.db.insert_substitution(sub)
    assert resp.css == Status("danger", "").css


def test_insert_substitution(app, test_login):
    sub = {}
    resp = app.db.insert_substitution(sub)
    assert resp.css == Status("success", "").css


def test_remove_substitution_anon(app):
    sub = {}
    resp = app.db.remove_substitution(sub)
    assert resp.css == Status("danger", "").css


def test_remove_substitution(app, test_login):
    sub = '5'
    resp = app.db.remove_substitution(sub)
    assert resp.css == Status("info", "").css


def test_get_from_pantry(app, mock_get_from_pantry):
    """Really just testing that errors don't happen"""
    data = None
    resp = app.db.find_all_matching_recipes(data)
    assert resp == []
    data = {
        "filters": {}
    }
    resp = app.db.find_all_matching_recipes(data)
    assert resp == []
    data = {
        "filters": {},
        "use_subs": "y"
    }
    resp = app.db.find_all_matching_recipes(data)
    assert resp == []


def test_get_from_pantry_login(app, test_login, mock_get_from_pantry):
    data = {
        "filters": {},
        "use_subs": "y"
    }
    resp = app.db.find_all_matching_recipes(data)
    assert resp == []
