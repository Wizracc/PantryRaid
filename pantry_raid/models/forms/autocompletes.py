"""Adapted from https://gist.github.com/doobeh/239b1e4586c7425e5114"""
from wtforms import StringField
from wtforms.widgets import HTMLString, html_params


class AutocompleteWidget():
    input_type = 'text'

    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', "input")
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()

        return HTMLString('<input {params}></input>'.format(
            params=self.html_params(name=field.name, **kwargs),
            label=field.label.text)
        )


class AutocompleteField(StringField):
    widget = AutocompleteWidget()
