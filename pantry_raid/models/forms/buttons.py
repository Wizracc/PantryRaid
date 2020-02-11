"""Adapted from https://gist.github.com/doobeh/239b1e4586c7425e5114"""
from wtforms import StringField
from wtforms.widgets import HTMLString, html_params


class ButtonWidget(object):
    """Renders a button. Pass HTML params, like `onclick`, as keyword arguments during instantiation."""
    html_params = staticmethod(html_params)

    def __call__(self, field, **kwargs):
        kwargs.setdefault('type', 'button')
        return HTMLString(f"<button {self.html_params(**kwargs)}>{field.label.text}</button>")


class CustomButton(StringField):
    """Button to add text field filter (pinned ingredients)"""
    widget = ButtonWidget()
