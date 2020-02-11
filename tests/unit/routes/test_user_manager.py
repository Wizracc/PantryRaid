"""
pantry_raid/routes/user_manager.py
"""
from flask import url_for
from pantry_raid.routes.user_manager import create_user, is_safe_url
from pytest import mark
pytestmark = mark.unit


def test_login(client, app, mock_render_template, mock_get_api):
    resp = client.get(url_for('user_manager.login'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_register(client, app, mock_render_template, mock_get_api):
    resp = client.get(url_for('user_manager.register'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_register_post(client, app, mock_render_template, mock_post_api):
    resp = client.post(url_for('user_manager.register_post'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_login_post(client, app, mock_render_template, mock_post_api):
    resp = client.post(url_for('user_manager.login_post'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"


def test_create_user(mock_regform, app):
    u = create_user(mock_regform)
    assert u.username == mock_regform.username.data
    assert u.email == mock_regform.email.data
    assert u.password != mock_regform.password.data


def test_is_safe_url(client):
    bad_url = "http://rude-website.org"
    bad_check = is_safe_url(bad_url)
    assert bad_check is False
    good_url = "index"
    good_check = is_safe_url(good_url)
    assert good_check is True


def test_register_post_form(client, app, packed_regform):
    resp = client.post(url_for('user_manager.register_post'), data=packed_regform, follow_redirects=True)
    assert "Logout</a>" in resp.data.decode('utf-8')
    dup_reg = dict(
        username="test",
        password="test",
        confirm_password="test"
    )
    bad_resp = client.post(url_for('user_manager.register_post'), data=dup_reg, follow_redirects=True)
    assert "already exists" in bad_resp.data.decode('utf-8')


def test_login_post_form(client, app):
    log = dict(
        username="test",
        password="test"
    )
    resp = client.post(url_for('user_manager.login_post'), data=log, follow_redirects=True)
    assert "Logout</a>" in resp.data.decode('utf-8')
    assert resp.status_code == 200


def test_login_malicious_redirect(client, app):
    log = dict(
        username="test",
        password="test"
    )
    resp = client.post(url_for('user_manager.login_post', next="http://bad.kitty"), data=log, follow_redirects=True)
    assert resp.status_code == 400
