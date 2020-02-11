# pytest configuration file containing fixtures
# Must exist in root directory for imports to work.
import json
import mongomock
import os
import pytest
from flask import jsonify, _request_ctx_stack
from mock import Mock
from pantry_raid import create_app
from pantry_raid.config import TestConfig

RESOURCE_PATH = os.path.join("tests", "resources")


"""Mock database for unit tests"""
@pytest.fixture
def app(monkeypatch):
    def fake_mongo(*args, **kwargs):
        return mongomock.MongoClient("mongodb://u:p@mongod:65535/test")

    monkeypatch.setattr('pantry_raid.models.database.Database.setup_mongoclient', fake_mongo)
    app = create_app(TestConfig)

    app.db.mongodb = fake_mongo().get_database('test')
    db = app.db.mongodb

    with open(os.path.join(RESOURCE_PATH, "ingredients.bson")) as bs:
        ing = db.create_collection("ingredients_v2")
        ing.insert_one(json.loads(bs.read()))

    with open(os.path.join(RESOURCE_PATH, "pantry.bson")) as bs:
        pant = db.create_collection("pantry")
        pant.insert_one(json.loads(bs.read()))

    with open(os.path.join(RESOURCE_PATH, "recipes.bson")) as bs:
        recip = db.create_collection("recipes_v2")
        for rec in json.loads(bs.read()):
            recip.insert_one(rec)

    with open(os.path.join(RESOURCE_PATH, "users.bson")) as bs:
        us = db.create_collection("users")
        us.insert_one(json.loads(bs.read()))

    # At this point, app.db's MongoCollection objects are still pointing towards empty collections and not the ones created above, so set them up
    app.db.pantry.collection = db.get_collection('pantry')
    app.db.users.collection = db.get_collection('users')
    app.db.ingredients.collection = db.get_collection('ingredients_v2')
    app.db.recipes.collection = db.get_collection('recipes_v2')
    return app


"""Test database for integration tests"""
@pytest.fixture
def integrated_app(monkeypatch):
    integrated_app = create_app(TestConfig)
    mongo = integrated_app.db.mongodb
    # Clear out any existing data and load the static data
    with open(os.path.join(RESOURCE_PATH, "ingredients.bson")) as bs:
        mongo.drop_collection("ingredients_v2")
        ing = mongo.create_collection("ingredients_v2")
        ing.insert_one(json.loads(bs.read()))

    with open(os.path.join(RESOURCE_PATH, "pantry.bson")) as bs:
        mongo.drop_collection("pantry")
        pant = mongo.create_collection("pantry")
        pant.insert_one(json.loads(bs.read()))

    with open(os.path.join(RESOURCE_PATH, "recipes.bson")) as bs:
        mongo.drop_collection("recipes_v2")
        recip = mongo.create_collection("recipes_v2")
        for rec in json.loads(bs.read()):
            recip.insert_one(rec)

    with open(os.path.join(RESOURCE_PATH, "users.bson")) as bs:
        mongo.drop_collection("users")
        us = mongo.create_collection("users")
        us.insert_one(json.loads(bs.read()))

    return integrated_app


"""Mock the Flask `client` for integration tests. The built-in `client` fixture from `pytest-flask` uses the `app` fixture, which is currently the mongomocked unit test one.

Modified from source code at https://github.com/pytest-dev/pytest-flask
"""
@pytest.yield_fixture
def integrated_client(integrated_app):
    with integrated_app.test_client() as integrated_client:
        yield integrated_client


@pytest.fixture
def integrated_config(integrated_app):
    return integrated_app.config


@pytest.fixture
def integrated_request_ctx(integrated_app):
    return _request_ctx_stack.top


def getfixturevalue(request, value):
    if hasattr(request, 'getfixturevalue'):
        return request.getfixturevalue(value)

    return request.getfuncargvalue(value)


@pytest.fixture(autouse=True)
def _integrated_push_request_context(request):
    """During tests execution request context has been pushed, e.g. `url_for`,
    `session`, etc. can be used in tests as is::
        def test_app(app, client):
            assert client.get(url_for('myview')).status_code == 200
    """
    if 'integrated_app' not in request.fixturenames:
        return

    integrated_app = getfixturevalue(request, 'integrated_app')

    if 'live_server' in request.fixturenames:
        integrated_app = getfixturevalue(request, 'live_server').app

    ctx = integrated_app.test_request_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)


@pytest.fixture(autouse=True)
def _integrated_configure_application(request, monkeypatch):
    if 'integrated_app' not in request.fixturenames:
        return

    integrated_app = getfixturevalue(request, 'integrated_app')
    for options in request.node.iter_markers('options'):
        for key, value in options.kwargs.items():
            monkeypatch.setitem(integrated_app.config, key.upper(), value)


"""End integrated pytest-flask"""


"""
Monkeypatch to mock out specific function returns down here. Use the below functions as examples if you need to add a mock. Unit tests should only test the function they call directly, not any functions that that function may call.

All should have the `@pytest.fixture` decorator and accept `monkeypatch` is the only argument. Then, create a nested function definition that takes `*args, **kwargs` and returns whatever mock value you need it to return.

After the nested function has been defined, use `monkeypatch.setattr` to hijack the function call. The first argument of `monkeypatch.setattr` needs to be a string: the full module path to the function name. Example: `pantry_raid.path.to.file.Class.function` for class functions, and the second argument should be the name of the nested function definition created above.

To ensure your test function uses the monkeypatched function, you simply pass the name of the monkeypatch fixture (not the nested function) to the test. A test will automatically apply any fixtures passed as arguments.
"""


@pytest.fixture
def mock_render_template(monkeypatch):
    """Mocking out render_template is necessary to keep tests from failing when the mock data return doesn't have all the variables Jinja needs to fill the template. Use this when you don't care about the contents of the template.
    """
    def mock_html(*args, **kwargs):
        return '<html>Fake</html>'

    monkeypatch.setattr('flask.templating._render', mock_html)


@pytest.fixture
def mock_get_api(monkeypatch):
    """Mock calls to pantry_raid.routes.api.get() to prevent inflating coverage when the API module isn't tested.
    """
    def mock_get(*args, **kwargs):
        return jsonify({"data": "got data"})

    monkeypatch.setattr('pantry_raid.routes.api.get', mock_get)


@pytest.fixture
def mock_post_api(monkeypatch):
    """Mock calls to pantry_raid.routes.api.post() to prevent inflating coverage when the API module isn't tested.
    """
    def mock_post(*args, **kwargs):
        return jsonify({"data": "posted data"})

    monkeypatch.setattr('pantry_raid.routes.api.post', mock_post)


@pytest.fixture
def test_user():
    u = Mock()
    u.username = "test"
    u.is_active = True
    # Not used, but required to actually access the real test user
    u.database = {
        '_id': 'test',
        'pantry': 'maggots',
        'substitutes': [
            "test"
        ]
    }
    u.get_id.return_value = u.username
    return u


@pytest.fixture
def mock_user(monkeypatch):
    def fake_user(*args, **kwargs):
        u = Mock()

        def mock_save():
            return True

        u.username = "dead"
        u.is_active = True
        u.database = {
            '_id': 'dead',
            'pantry': 'maggots'
        }
        u.save = mock_save

    monkeypatch.setattr('pantry_raid.models.user.User.__init__', fake_user)


@pytest.fixture
def test_login(app, test_user):
    @app.logman.request_loader
    def load_user_from_request(request):
        return test_user
    return True


@pytest.fixture
def mock_regform():
    f = Mock()
    f.username.data = "no"
    f.password.data = "nono"
    f.confirm_password.data = "nono"
    f.email.data = "spam@spam.cx"
    f.validate_on_submit.return_value = True
    return f


@pytest.fixture
def packed_regform(mock_regform):
    return dict(username=mock_regform.username.data,
                password=mock_regform.password.data,
                confirm_password=mock_regform.confirm_password.data,
                email=mock_regform.email.data)


@pytest.fixture
def mock_get_from_pantry(monkeypatch):
    def mocka(*args, **kwargs):
        return []

    monkeypatch.setattr('pantry_raid.models.recipes.Recipes.get_from_pantry', mocka)
