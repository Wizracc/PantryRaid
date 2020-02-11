from flask_wtf import FlaskForm as Form
from wtforms import BooleanField, FieldList, IntegerField, SelectField, SelectMultipleField, StringField, SubmitField
from pantry_raid.models.forms.buttons import CustomButton


class SearchForm(Form):
    """Search form, including filters.

    Filters must be instantiated with the `render_kw` keyword in the top-most element and this should be a dictionary containing at least two fields: `mongo_operator` and `mongo_field`, corresponding to the operator and collection field that the filter pertains to.

    The top-most element of a `FieldList` is the `FieldList` itself. For example, with `FieldList(SomeField())`, the `render_kw` must be part of `FieldList`'s arguments, *not* `SomeField`'s.
    """
    pinned_ingredients = FieldList(StringField(),
        render_kw={
            "autocomplete": "off",
            "mongo_operator": "$all",
            "mongo_field": "ingredient_names",
        }
    )
    add_pinned = CustomButton("<i class=\"fas fa-plus-circle\"></i>")

    excluded_ingredients = FieldList(StringField(),
        render_kw={
            "autocomplete": "off",
            "mongo_operator": "$nin",
            "mongo_field": "ingredient_names",
        }
    )
    add_excluded = CustomButton("<i class=\"fas fa-plus-circle\"></i>")

    prep_time = IntegerField("Prep Time in minutes \u2264", render_kw={
        "autocomplete": "off",
        "mongo_operator": "$lte",
        "mongo_field": "prep_time_minutes"
    })

    macronutrients = SelectField(
        label="Macronutrient",
        choices=[
            ("calories", "Calories"), ("grams fat", "Grams Fat"),
            ("grams carbohydrates", "Grams Carbohydrates"),
            ("grams protein", "Grams Protein"),
            ("milligrams cholesterol", "Milligrams Cholesterol"),
            ("milligrams sodium", "Milligrams Sodium")
        ]
    )

    macronutrient_value = IntegerField("Value", render_kw={
        "autocomplete": "off",
        "mongo_operator": "compare value",
        "mongo_field": "placeholder"
    })

    compare_options = SelectField(
        label="Compare",
        choices=[
            ("$lte", "\u2264"), ("$gte", "\u2265")
        ]
    )

    use_subs = BooleanField("Use Ingredient Substitutions")

    sort_options = SelectField(
        label="Sort",
        choices=[
            ("abc+", "Alphabetically, ascending"), ("abc-", "Alphabetically, descending"),
            ("cal+", "Calories, ascending"), ("cal-", "Calories, descending"),
            ("fat+", "Grams Fat, ascending"), ("fat-", "Grams Fat, descending"),
            ("carb+", "Grams Carbs, ascending"), ("carb-", "Grams Carbs, descending"),
            ("prot+", "Grams Protein, ascending"), ("prot-", "Grams Protein, descending"),
            ("chol+", "Milligrams Cholesterol, ascending"), ("chol-", "Milligrams Cholesterol, descending"),
            ("na+", "Milligrams Sodium, ascending"), ("na-", "Milligrams Sodium, descending")
        ]
    )

    tags = SelectMultipleField(
        label="Tags",
        choices=[]  # Filled in on demand in the template
    )

    submit = SubmitField("Search", render_kw={ "style": "width: 100%; display: block; height: 5em" })
