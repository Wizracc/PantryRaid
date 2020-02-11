"""
pantry_raid/routes/routes.py
Test fronted routing here.

These tests are to verify that the routing functions work properly. Since these functions are meant to grab data from the JSON API and then render a template, the tests don't need to do much other than check status codes. Verifying the data should be done in test_api.py instead, since it's far easier to compare JSON expected values than entire HTML pages.

Test resources might need to be updated whenever they change, for example, updates to the template or the test data used.
"""
import mock
from flask import url_for
from pytest import mark
pytestmark = mark.unit


def test_root(client, app, mock_render_template, mock_get_api):
    resp = client.get('/')
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_search(client, app, mock_render_template, mock_get_api):
    resp = client.get(url_for('routes.search'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_pantry(client, app, mock_render_template, mock_get_api):
    resp = client.get(url_for('routes.pantry'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_pantry_post(client, app, mock_render_template, mock_post_api):
    resp = client.post(url_for('routes.pantry_post'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_about(client, app, mock_render_template, mock_get_api):
    resp = client.get(url_for('routes.about'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_help(client, app, mock_render_template, mock_get_api):
    resp = client.get(url_for('routes.help'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_all_recipes(client, app, mock_render_template, mock_get_api):
    resp = client.get(url_for('routes.all_recipes'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_bad_recipes(client, app):
    for bad in ['fake', float('inf'), float('-inf')]:
        resp = client.get(url_for('routes.recipe', rid=bad))
        assert resp.status_code == 404
        assert resp.mimetype == "text/html"


def test_specific_recipe(client, app, mock_render_template):
    rid = '16715'
    resp = client.get(url_for('routes.recipe', rid=rid))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_substitute(client, app, mock_render_template):
    resp = client.get(url_for('routes.substitute'))
    assert resp.status_code == 302
    assert resp.mimetype == "text/html"


def test_substitute_post(client, app, mock_render_template, mock_post_api):
    resp = client.post(url_for('routes.substitute'))
    assert resp.status_code == 302
    assert resp.mimetype == "text/html"


def test_favorites(client, app, mock_render_template, test_login):
    resp = client.get(url_for('routes.favorite_recipes'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_recipe_post(client, app, mock_render_template, test_login):
    pre_favs = app.db.get_favorites()
    client.post(url_for('routes.recipe_post', rid='555'))
    post_favs = app.db.get_favorites()
    assert len(pre_favs) == len(post_favs) - 1
    # Repeating the post with the same ID will remove it if it's in favorites
    client.post(url_for('routes.recipe_post', rid='555'))
    rm_favs = app.db.get_favorites()
    assert len(pre_favs) == len(rm_favs)


def test_substitute_logged(client, app, mock_render_template, test_login):
    resp = client.get(url_for('routes.substitute'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_all_tags(client, app, mock_render_template):
    resp = client.get(url_for('routes.all_tags'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_tags(client, app, mock_render_template):
    resp = client.get(url_for('routes.tags', tag="chicken"))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"
