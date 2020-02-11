from flask_wtf import FlaskForm as Form
from wtforms import SubmitField
from pantry_raid.models.forms.autocompletes import AutocompleteField


class PantryForm(Form):
    add_food = AutocompleteField("Add Items to Pantry")
    submit = SubmitField("Add", render_kw={
        "style": "width: 100%; height: 5em;"
    })
