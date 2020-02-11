"""
pantry_raid/models/MongoCollection.py

Since this is an abstract class, it must be tested using one of its descendants.
"""
from pytest import mark
pytestmark = mark.int


def test_get_subset(integrated_app):
    pantry = [
        "all-purpose flour",
        "eggs",
        "milk",
        "butter",
        "water",
        "salt"
    ]
    results = integrated_app.db.recipes.get_subset("ingredient_names", pantry, None)
    assert len(results) == 1
    assert results[0]['name'] == "MOCK Basic Crepes"


def test_get_subset_with_fake_filter(integrated_app):
    filt = {
        "some_filter": {
            "items": [],
            "mongo_operator": "$all",
            "mongo_field": "hedgehog"
        }
    }
    results = integrated_app.db.recipes.get_subset("ingredient_names", integrated_app.db.pantry.get_as_list(), filt)
    assert len(results) == 3  # Easy Quiche, Puff Pastry Waffles, Crustless Spinach Quiche


def test_get_subset_with_real_filter(integrated_app):
    filt = {
        "filters": {
            "pinned_ingredients": {
                "items": [ "butter" ],
                "mongo_operator": "$all",
                "mongo_field": "ingredient_names"
            }
        },
        "tags": [],
        "sort_options": "abc+"
    }
    results = integrated_app.db.recipes.get_subset("ingredient_names", integrated_app.db.pantry.get_as_list(), filt)
    assert len(results) == 1  # Easy Quiche
