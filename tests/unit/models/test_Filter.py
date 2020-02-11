"""
pantry_raid/models/filter.py
"""
from pantry_raid.models.filter import Filter
from pytest import mark
pytestmark = mark.unit


def test_init():
    q_doc = {
        "ingredient_names": {
            "$all": [ "cheese wheel", "super mushroom" ],
            "$nin": [ "reznor", "torpedo ted", "bullet bill" ]
        }
    }

    fild = {
        "pinned_ingredients": {
            "items": [ "cheese wheel", "super mushroom" ],
            "mongo_operator": "$all",
            "mongo_field": "ingredient_names"
        },
        "excluded_ingredients": {
            "items": [ "reznor", "torpedo ted", "bullet bill" ],
            "mongo_operator": "$nin",
            "mongo_field": "ingredient_names",
            "k": "v"
        }
    }

    res = Filter(fild)
    assert res.doc == q_doc
