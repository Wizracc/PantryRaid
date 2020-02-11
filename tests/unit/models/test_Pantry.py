"""
pantry_raid/models/Pantry.py
"""
from pantry_raid.models.pantry import Pantry
from pantry_raid.models.status import Status
from pytest import mark
pytestmark = mark.unit


def test_init(app):
    collection = app.db.mongodb['pantry']
    pan = Pantry(collection)
    assert pan.collection_key == "pantry"


def test_get_partial_match_recipes(app):
    pm = app.db.pantry.get_partial_match_recipes(app.db.recipes)
    assert len(pm) == 101
    # find some recipe in list of dicts, default to None if not found
    ty = next((r for r in pm if r["name"] == "MOCK Cobb Salad"), None)
    assert ty is not None


def test_get_complete_match_recipes(app):
    recipes = app.db.recipes
    results = app.db.pantry.get_complete_match_recipes(recipes)
    assert len(results) == 3
    one = next((r for r in results if "MOCK" in r["name"]), None)
    assert one is not None


def test_insert_new_ingredient(app):
    new = "food"
    ok = app.db.pantry.insert_new_ingredient(new)
    assert ok == Status("success", f"Added {new} to your pantry.")


def test_remove_ingredient(app):
    rm = "onion"
    ok = app.db.pantry.remove_ingredient(rm)
    assert ok == Status("info", f"Removed {rm} from your pantry.")
