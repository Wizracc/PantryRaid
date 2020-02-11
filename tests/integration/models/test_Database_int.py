"""
pantry_raid/models/Database.py
"""
from pytest import mark
pytestmark = mark.int


def test_find_all_matching_recipes(integrated_app):
    db_find = integrated_app.db.find_all_matching_recipes()
    pantry_find = integrated_app.db.pantry.get_complete_match_recipes(integrated_app.db.recipes)
    for doc in db_find:
        assert doc in pantry_find
