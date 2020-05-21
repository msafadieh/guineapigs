"""
    forms for logged out users
"""
from wtforms.fields import StringField
from wtforms.form import Form
from wtforms.validators import DataRequired


class LoginForm(Form):  # pylint: disable=too-few-public-methods
    """
    fields:
        - name: str
    """

    name = StringField(
        label="first name", validators=[DataRequired("name can't be blank")]
    )
