"""
pantry_raid/models/ingredients.py
"""
from pantry_raid.models.ingredients import Ingredients
from pytest import mark
pytestmark = mark.unit


def test_init(app):
    collection = app.db.mongodb['ingredients']
    ing = Ingredients(collection)
    assert ing.collection_key == "ingredients"
