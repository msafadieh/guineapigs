from sqlalchemy.ext.declarative import declared_attr
from guineapigs.app import app, db
from datetime import datetime
import pytz

__all__ = ('User', 'GuineaPig', 'FoodType', 'FoodEntry', 'VitaminCEntry', 'WeightEntry', )

food_entries = db.Table('food_entries',
        db.Column('food_entry_id', db.Integer, db.ForeignKey('food_entry.id'), primary_key=True),
        db.Column('guinea_pig_id', db.Integer, db.ForeignKey('guinea_pig.id'), primary_key=True),
)

class User(db.Model):
    __tablename__ = 'user'
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
    __tablename__ = 'guinea_pig'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    food_entries = db.relationship("FoodEntry", secondary=food_entries)
    weight_entries = db.relationship("WeightEntry")

class FoodType(db.Model):
    __tablename__ = 'food_type'
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), nullable=False) 
    recommendations = db.Column(db.String(512))
    entries = db.relationship("FoodEntry")

class Entry:

    @declared_attr
    def user_id(cls):
        return db.Column(db.Integer, db.ForeignKey('user.id'))

    utc_date = db.Column(db.DateTime, default=lambda: datetime.utcnow())
    @classmethod
    def get_entries_from_today(cls):
        timezone = app.config["TIMEZONE"]
        start_of_day = datetime.now()\
                                .astimezone(timezone)\
                                .replace(hour=0,
                                         minute=0,
                                         second=0,
                                         microsecond=0)

        return cls.query.filter(cls.utc_date >= start_of_day)

class FoodEntry(db.Model, Entry):
    __tablename__ = 'food_entry'
    id = db.Column(db.Integer, primary_key=True)
    food_type_id = db.Column(db.Integer, db.ForeignKey('food_type.id'), nullable=False)
    food_type = db.relationship('FoodType')
    notes = db.Column(db.String(512))
    guinea_pigs = db.relationship("GuineaPig", secondary=food_entries)
    user = db.relationship('User')

class VitaminCEntry(db.Model, Entry):
    __tablename__ = 'vitamin_c_entry'
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User')

class WeightEntry(db.Model, Entry):
    __tablename__ = 'weight_entry'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    guinea_pig_id = db.Column(db.Integer, db.ForeignKey("guinea_pig.id"), nullable=False)
    user = db.relationship('User')
