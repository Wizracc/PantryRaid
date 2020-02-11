from flask_wtf import FlaskForm as Form
from wtforms import FieldList, FormField, SubmitField, StringField
from pantry_raid.models.forms.autocompletes import AutocompleteField
from pantry_raid.models.forms.buttons import CustomButton


class SubstituteField(Form):
    quantity = StringField("Quantity", render_kw={
        "id": "sub_qty",
        "placeholder": "Quantity",
        "style": "width: 100%; max-width: 40%;"
    })
    ingredient = AutocompleteField("Ingredient", render_kw={
        "id": "sub_ingredient",
        "placeholder": "Ingredient",
        "style": "width: 100%; max-width: 40%;"
    })


class SubstitutionForm(Form):
    add_target = AutocompleteField("Target Ingredient", render_kw={
        "id": "target",
        "numIngredients": 0,
        "autocomplete": "off"
    })
    target_qty = StringField("Target Quantity", render_kw={
        "id": "target_qty"
    })
    substitute = FieldList(FormField(SubstituteField), min_entries=1)
    add_ingredient = CustomButton("<i class=\"fas fa-plus-circle\"></i>")
    submit = SubmitField("Add Substitution", render_kw={
        "style": "width: 100%; height: 5em"
    })
