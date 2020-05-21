"""
    forms for logged in users
"""
from flask_wtf import FlaskForm
from wtforms.fields import DateField, SelectField, SelectMultipleField
from wtforms.form import Form
from wtforms.validators import DataRequired
from wtforms_alchemy import model_form_factory
from guineapigs import models

ModelForm = model_form_factory(FlaskForm)


class GuineaPigForm(ModelForm):  # pylint: disable=too-few-public-methods
    """
    fields:
        - name: str
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
            maps to GuineaPig model
        """

        model = models.GuineaPig


class FoodTypeForm(ModelForm):  # pylint: disable=too-few-public-methods
    """
    fields:
        - label: str
        - recommendations: str
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
            maps to FoodType model
        """

        model = models.FoodType


class FoodEntryForm(ModelForm):  # pylint: disable=too-few-public-methods
    """
    fields:
        - food_type_id: int
        - guinea_pigs_ids: [int]
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
            maps to FoodEntry model
        """

        model = models.FoodEntry

    food_type_id = SelectField("food", coerce=int)
    guinea_pig_ids = SelectMultipleField("guinea pigs", coerce=int)


class WeightEntryForm(ModelForm):  # pylint: disable=too-few-public-methods
    """
    fields:
        - value: float
        - guinea_pigs_id: int
    """

    class Meta:  # pylint: disable=too-few-public-methods
        """
            maps to WeightEntry model
        """

        model = models.WeightEntry

    guinea_pig_id = SelectField("guinea Pigs", coerce=int)


class HistoryForm(Form):  # pylint: disable=too-few-public-methods
    """
    fields:
        - start: date
        - end: date
    """

    start = DateField(label="start", validators=[DataRequired()])
    end = DateField(label="end", validators=[DataRequired()])
