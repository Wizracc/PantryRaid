class Status(object):
    """Wrapper around a dictionary representing styled status text.

    Attributes
    ----------
    text : string
        Message describing the status

    css : string
        CSS classes to apply to `text`. The first word should be a Bulma class (danger, info, success, warning) that is concatenated with the `has-text-` prefix to color the text. Other classes may be applied as space-separated values.
    """
    def __init__(self, css, text):
        self.text = text
        self.css = f"has-text-{css}"

    def __eq__(self, other):
        return self.text == other.text and self.css == other.css
