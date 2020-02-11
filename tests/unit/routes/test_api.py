"""
pantry_raid/routes/api.py
Test backend JSON routing here.
"""
import copy
from flask import url_for
import json
import os
from pantry_raid.routes.api import all_recipes, get, pantry_post, post, substitute_post
from pytest import mark, raises
pytestmark = mark.unit


RESOURCE_PATH = os.path.join(*["tests", "resources"])
with open(os.path.join(RESOURCE_PATH, "recipes.bson")) as rec:
    all_rec = json.loads(rec.read())
with open(os.path.join(RESOURCE_PATH, "pantry.bson")) as pan:
    pantry = json.loads(pan.read())


def test_from_bson():
    pass


def test_get(client):
    resp = get(all_recipes)
    assert resp == client.get(url_for('api.all_recipes')).json


def test_all_recipes(client):
    resp = client.get(url_for('api.all_recipes'))
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert resp.json == all_rec


def test_recipe(client):
    rid = "20876"
    resp = client.get(url_for('api.recipe', arg=rid))
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    match = next((r for r in all_rec if rid == r["id"]), None)
    assert resp.json == match

    empty = "-1"
    empty_resp = client.get(url_for('api.recipe', arg=empty))
    assert empty_resp.status_code == 200
    assert empty_resp.json is None


def test_pantry(client):
    resp = client.get(url_for('api.pantry'))
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert sorted(resp.json['pantry']) == sorted(pantry['pantry'])


def test_pantry_post(client):
    """Flask doesn't take well to accept arguments in url_for for post, so this is the best this test can be for now.
    """
    nu = { "add_food": "quinoa" }
    new_pantry = copy.deepcopy(pantry)
    resp = post(pantry_post, nu)
    new_pantry['pantry'].append(nu["add_food"])
    assert sorted(resp['pantry']) == sorted(new_pantry['pantry'])
    assert resp['status']['css'] == "has-text-success"

    bad = { "add_food": "fake" }
    bad_resp = post(pantry_post, bad)
    assert bad_resp['status']['css'] == "has-text-danger"

    with raises(IndexError):
        post(pantry_post, {})


def test_substitute(client):
    data = {
        "remove_ingredient_index": "5"
    }
    resp = substitute_post(data)
    assert resp.status_code == 200
    data = {}
    resp = substitute_post(data)
    assert resp.status_code == 200
