from flask_wtf import FlaskForm
from wtforms.fields import SelectField, SelectMultipleField, StringField
from wtforms.validators import DataRequired
from wtforms.widgets import CheckboxInput, ListWidget
from wtforms_alchemy import model_form_factory
from guineapigs.models import *

ModelForm = model_form_factory(FlaskForm)

# https://wtforms.readthedocs.io/en/2.3.x/specific_problems/#specialty-field-tricks
class MultiCheckboxField(SelectMultipleField):
    """
    A multiple-select, except displays a list of checkboxes.

    Iterating the field will produce subfields, allowing custom rendering of
    the enclosed checkbox fields.
    """
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class GuineaPigForm(ModelForm):
    class Meta:
        model = GuineaPig

class FoodTypeForm(ModelForm):
    class Meta:
        model = FoodType

class FoodEntryForm(ModelForm):
    class Meta:
        model = FoodEntry
    food_type_id = SelectField("Food", coerce=int)
    guinea_pig_ids = MultiCheckboxField("Guinea Pigs", coerce=int)

class WeightEntryForm(ModelForm):
    class Meta:
        model = WeightEntry
    guinea_pig_id = SelectField("Guinea Pigs", coerce=int)

class LoginForm(ModelForm):
    name = StringField(label="First Name", validators=[DataRequired("Name can't be blank")])

