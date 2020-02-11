"""
pantry_raid/models/pipeline.py
"""
from pantry_raid.models.filter import Filter
from pantry_raid.models.pipeline import Pipeline
from pytest import mark
pytestmark = mark.unit


def test_init():
    p = Pipeline()
    assert p.operations == []


def test_add_filter():
    p = Pipeline()
    assert p.operations == []
    f = Filter(
        {
            "excluded_ingredients": {
                "items": [ "reznor", "torpedo ted", "bullet bill" ],
                "mongo_operator": "$nin",
                "mongo_field": "ingredient_names",
                "k": "v"
            }
        }
    )
    p.add_filter(f)
    assert p.operations == [
        {
            "$match": f.doc
        }
    ]


def test_add_operation_by_kvp():
    p = Pipeline()
    assert p.operations == []
    operator = "$operator"
    operand = {
        "tacticool": "innawoods"
    }
    p.add_operation_by_kvp(operator, operand)
    assert p.operations == [
        {
            operator: operand
        }
    ]


def test_remove__id():
    p = Pipeline()
    assert p.operations == []
    p.remove__id()
    assert p.operations == [ { "$project": { "_id": False } }]
