"""
pantry_raid/models/recipes.py
"""
from pytest import mark
pytestmark = mark.unit


def test_get_all_using(app):
    docs = app.db.recipes.get_all_using("butter")
    assert len(docs) == 37


def test_get_by_id(app):
    doc = app.db.recipes.get_by_id("98579")
    assert doc['name'] == "MOCK Barbie's Tuna Salad"
