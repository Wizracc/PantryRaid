import re
import json
import sys
from itertools import chain


# Make sure periods are escaped
def escape_re_string(text):
    text = text.replace('.', '\.')
    return re.sub(r'\s+', ' ', text)


# Dictionary of units
UNITS = { "cup": ["cups", "cup", "c.", "c"],
          "fluid_ounce": ["fl. oz.", "fl oz", "fluid ounce", "fluid ounces"],
          "gallon": ["gal", "gal.", "gallon", "gallons"],
          "ounce": ["oz", "oz.", "ounce", "ounces"],
          "pint": ["pt", "pt.", "pint", "pints"],
          "pound": ["lb", "lb.", "pound", "pounds"],
          "quart": ["qt", "qt.", "qts", "qts.", "quart", "quarts"],
          "tablespoon": ["tbsp.", "tbsp", "T", "T.", "tablespoon",
                         "tablespoons", "tbs.", "tbs"],
          "teaspoon": ["tsp.", "tsp", "t", "t.", "teaspoon", "teaspoons"],
          "gram": ["g", "g.", "gr", "gr.", "gram", "grams"],
          "kilogram": ["kg", "kg.", "kilogram", "kilograms"],
          "liter": ["l", "l.", "liter", "liters"],
          "milligram": ["mg", "mg.", "milligram", "milligrams"],
          "milliliter": ["ml", "ml.", "milliliter", "milliliters"],
          "pinch": ["pinch", "pinches"],
          "dash": ["dash", "dashes"],
          "touch": ["touch", "touches"],
          "handful": ["handful", "handfuls"],
          "stick": ["stick", "sticks"],
          "clove": ["cloves", "clove"],
          "can": ["cans", "can"],
          "small": ["small"],
          "scoop": ["scoop", "scoops"],
          "filets": ["filet", "filets"],
          "sprig": ["sprigs", "sprig"],
          "package": ["package", "packages"],
          "slice": ["slice", "slices"],
          "container": ["container", "containers", "can or bottle"],
          "drop": ["drop", "drops"],
          "inch": ["inch", "inches"],
          "head": ["head", "heads"],
          "bag": ["bag", "bags"],
          "stalk": ["stalk", "stalks"],
          "bottle": ["bottle", "bottles"],
          "bulb": ["bulb", "bulbs"],
          "bunch": ["bunch", "bunches"],
          "jar": ["jar", "jars"],
          "piece": ["piece", "pieces"]
        }

# unit notes, for adjectives on units
UNIT_NOTES = ["thick", "big", "large"]

# ingredient notes, for adjectives or other notes on ingredients
ING_NOTES = ["whole skinless, boneless", "boneless skinless", "peeled and chopped",
             "mashed cooked", "frozen", "chopped", "diced and chilled, cooked",
             "diced", "minced", "grated", "cubed", "fresh", "sliced", "bulk",
             "peeled and diced", "raw", "very ripe", "miniature", "canned",
             "packed", "finely crushed", "dried", "ripe", "cooked, diced",
             "chopped, cooked", "ground", "shredded", "medium",
             "hard-cooked", "prepared", "uncooked", "skinless, boneless",
             "peeled", "halved", "cubed, cooked", "crushed", "leftover",
             "thinly sliced", "freshly ground", "softened"]

# Create list from unit aliases
a = list(chain.from_iterable(UNITS.values()))
# Sort the list, because that's what the other parser did,
# I'm sure there's a good reason
a.sort(key=lambda x: len(x), reverse=True)
# Escape the periods so it can be used in regex
a = map(escape_re_string, a)

amount = r"\d*(?:\.\d+)?(?:\s?\d+/\d+)?"
units = "|".join(a)
unit_notes = "|".join(UNIT_NOTES)
ing_notes = r"(?:(?:{0})\s?)+".format("|".join(ING_NOTES))
ings = r"(?:(?:\w|\w-\w|')+\s?)+\w"
prep_reg = r"(?:\w*,?\s?)+\w"
prep_notes = r"(?:\s\(({0})\))|(?:\s-\s({0}))|(?:,\s({0}))|(?:\s(to taste))".format(prep_reg)

pattern = (r"^(?:(?:({0})\s)?(?:\(({0})\s({1})\)\s)?(?:({2})\s)?(?:({1})\s)?" +
           "(?:({3})\s)?(?:(?:({4}))(?=(?:({5}))))?({4})?)")\
           .format(amount, units, unit_notes, ing_notes, ings, prep_notes)

reg = re.compile(pattern)


def parse(string):
    result = reg.match(string)
    ing_dict = {}
    if result is not None:
        outer_amount = result.group(1)  # Amount
        inner_amount = result.group(2)  # Inner Amount
        inner_unit = result.group(3)  # Inner Unit
        unit_notes = result.group(4)  # Unit Notes
        unit = result.group(5)  # Unit
        ing_notes = result.group(6)  # Ingredient Notes
        ingredients = result.group(7)  # Ingredient (may not be present, see group 13)
        prep_notes = ""
        if ingredients is not None:
            raw_prep_notes = result.group(8)  # raw Prep Notes (may not be present, see group 13)
            if result.group(9) is not None:
                prep_notes = result.group(9)  # (Prep Notes)
            elif result.group(10) is not None:
                prep_notes = result.group(10)  # , Prep Notes
            elif result.group(11) is not None:
                prep_notes = result.group(11)  # - Prep Notes
            else:
                prep_notes = result.group(12)  # to taste - Prep Notes
        else:
            ingredients = result.group(13)  # If prep notes present, is raw prep notes, else is Ingredients
        # SPECIAL CASES
        if ingredients == "white bread cubes":
            ingredients = "white bread"
            prep_notes = "cubes"
        elif ingredients == "pita bread rounds":
            ingredients = "pita bread"
            prep_notes = "rounds"
        elif ingredients == "vegetable shortening for deep frying":
            ingredients = "vegetable shortening"
            prep_notes = "for deep frying"
        elif ingredients == "corned beef briskets with spice packets":
            ingredients = "corned beef briskets"
            prep_notes = "with spice packets"
        elif ingredients == "roma or plum tomato":
            ingredients == "tomato"
            prep_notes = "roma or plum"

        ing_dict = {
            "string": string,
            "outer_amount": outer_amount,
            "inner_amount": inner_amount,
            "inner_unit": inner_unit,
            "unit_notes": unit_notes,
            "outer_unit": unit,
            "ingredient_notes": ing_notes,
            "ingredients": ingredients,
            "prep_notes": prep_notes
        }

    return ing_dict
