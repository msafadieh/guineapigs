"""
    declarations of HTML forms to get user data
"""
from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SelectMultipleField, StringField
from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms_alchemy import model_form_factory
from guineapigs.models import *

__all__ = (
    "GuineaPigForm",
    "FoodTypeForm",
    "FoodEntryForm",
    "WeightEntryForm",
    "LoginForm",
)

ModelForm = model_form_factory(FlaskForm)


class GuineaPigForm(ModelForm):
    """
    fields:
        - name: str
    """

    class Meta:
        model = GuineaPig


class FoodTypeForm(ModelForm):
    """
    fields:
        - label: str
        - recommendations: str
    """

    class Meta:
        model = FoodType


class FoodEntryForm(ModelForm):
    """
    fields:
        - food_type_id: int
        - guinea_pigs_ids: [int]
    """

    class Meta:
        model = FoodEntry

    food_type_id = SelectField("food", coerce=int)
    guinea_pig_ids = SelectMultipleField("guinea pigs", coerce=int)


class WeightEntryForm(ModelForm):
    """
    fields:
        - value: float
        - guinea_pigs_id: int
    """

    class Meta:
        model = WeightEntry

    guinea_pig_id = SelectField("guinea Pigs", coerce=int)


class LoginForm(ModelForm):
    """
    fields:
        - name: str
    """

    name = StringField(
        label="first name", validators=[DataRequired("name can't be blank")]
    )
