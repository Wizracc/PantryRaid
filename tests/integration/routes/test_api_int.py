"""
pantry_raid/routes/api.py
"""
from flask import url_for
from pytest import mark
pytestmark = mark.int


def test_search_post(integrated_client):
    resp = integrated_client.post(url_for('api.search_post'))
    assert resp.status_code == 200
    assert resp.mimetype == 'application/json'
    assert len(resp.json) == 3  # test pantry only gets 3 results
