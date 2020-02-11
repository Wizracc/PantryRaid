"""
pantry_raid/models/mongocollection.py

Since this is an abstract class, we need to test it using its inheritors.
"""
from pytest import mark
pytestmark = mark.unit


def test_get_as_list(app):
    with_key = app.db.pantry
    wk = with_key.get_as_list()
    assert type(wk) == list
    assert "MOCK_PANTRY" in wk

    without_key = app.db.recipes
    wok = without_key.get_as_list()
    assert type(wok) == list
    assert type(wok[0]) == dict
    one = next((r for r in wok if "MOCK" in r["name"]), None)
    assert one is not None


def test_flatten_nested_dict_lists(app):
    mc = app.db.recipes
    caw = [
        [
            { "bird": "crow" },
            { "bird": "raven"}
        ],
        [
            { "bird": "osprey" },
            { "bird": "eagle" }
        ]
    ]
    assert len(caw) == 2
    splat = mc.flatten_nested_dict_lists(caw)
    assert len(splat) == 4
    assert splat == [
        { "bird": "crow" },
        { "bird": "raven" },
        { "bird": "osprey" },
        { "bird": "eagle" }
    ]
    splatter = mc.flatten_nested_dict_lists(splat)
    # Shouldn't do anything to already flattened lists
    assert splatter == splat


def test_deduplicate_document_list(app):
    mc = app.db.recipes
    caw = [
        { "id": "crow" },
        { "id": "crow" },
        { "id": "crow" },
        { "id": "crow" },
        { "id": "crow" },
        { "id": "crow" },
        { "id": "raven" },
        { "id": "raven" },
        { "id": "osprey" },
        { "id": "osprey" },
        { "id": "eagle" },
        { "id": "eagle" }
    ]
    cull = mc.deduplicate_document_list(caw)
    assert len(cull) == 4
    assert cull == [
        { "id": "crow" },
        { "id": "raven" },
        { "id": "osprey" },
        { "id": "eagle" }
    ]
