"""
pantry_raid/routes/routes.py
"""
from flask import url_for
import os
from pytest import mark
pytestmark = mark.int


RESOURCE_PATH = os.path.join(*["tests", "resources"])


def test_search_results(integrated_client):
    resp = integrated_client.post(url_for('routes.search'))
    assert resp.status_code == 200
    assert resp.mimetype == "text/html"
