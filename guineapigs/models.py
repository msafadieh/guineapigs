"""
    Database models and tables
"""
from sqlalchemy.ext.declarative import declared_attr
from guineapigs.app import app, db
from guineapigs.utils import beginning_of_day_utc
from datetime import datetime

__all__ = (
    "User",
    "GuineaPig",
    "FoodType",
    "FoodEntry",
    "VitaminCEntry",
    "WeightEntry",
    "food_entries",
)

food_entries = db.Table(
    "food_entries",
    db.Column(
        "food_entry_id", db.Integer, db.ForeignKey("food_entry.id"), primary_key=True
    ),
    db.Column(
        "guinea_pig_id", db.Integer, db.ForeignKey("guinea_pig.id"), primary_key=True
    ),
)


class User(db.Model):
    """
    A user has a name and no password
    """

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    food_entries = db.relationship("FoodEntry")
    weight_entries = db.relationship("WeightEntry")

    def get_id(self):
        return str(self.id)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False


class GuineaPig(db.Model):
    """
    Guinea pig model to keep track of food and weight for each
    """

    __tablename__ = "guinea_pig"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    food_entries = db.relationship("FoodEntry", secondary=food_entries)
    weight_entries = db.relationship("WeightEntry")


class FoodType(db.Model):
    """
    Type of food to be used with the entry (and recommendations on it) 
    """

    __tablename__ = "guinea_pig"
    __tablename__ = "food_type"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), nullable=False)
    recommendations = db.Column(db.String(512))
    entries = db.relationship("FoodEntry")
    in_statistics = db.Column(db.Boolean, nullable=False, default=True, info={'label': 'in statistics'})
    is_hidden = db.Column(db.Boolean, nullable=False, default=False, info={'label': 'is hidden'})

class Entry:
    """
    Entry base class that defines a user_id foreign key and timestamp
    """

    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey("user.id"))

    @declared_attr
    def user(cls):
        return db.relationship("User")

    utc_date = db.Column(db.DateTime, default=datetime.utcnow)


class FoodEntry(db.Model, Entry):
    """
    A food entry can have many guinea pigs
    """

    __tablename__ = "food_entry"
    id = db.Column(db.Integer, primary_key=True)
    food_type_id = db.Column(db.Integer, db.ForeignKey("food_type.id"), nullable=False)
    food_type = db.relationship("FoodType")
    notes = db.Column(db.String(512))
    guinea_pigs = db.relationship("GuineaPig", secondary=food_entries)


class VitaminCEntry(db.Model, Entry):
    """
    Vitamin C entries only have users and timestamps
    """

    __tablename__ = "vitamin_c_entry"
    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_today(cls):
        return VitaminCEntry.query.filter(
            VitaminCEntry.utc_date >= beginning_of_day_utc()
        ).first()


class WeightEntry(db.Model, Entry):
    """
    Weight entries can only have one guineapig
    """

    __tablename__ = "weight_entry"
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    guinea_pig_id = db.Column(
        db.Integer, db.ForeignKey("guinea_pig.id"), nullable=False
    )
