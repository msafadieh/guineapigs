"""
    Database models and tables
"""
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from guineapigs.extensions import db
from guineapigs.utils import beginning_of_day_utc

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
        """
        returns user id as a str
        """
        return str(self.id)

    @staticmethod
    def is_authenticated():
        """
        returns user is always authenticated (for now at least)
        """
        return True

    @staticmethod
    def is_active():
        """
        returns user is always active
        """
        return True

    @staticmethod
    def is_anonymous():
        """
        returns False as user is never anonymous
        """
        return False


class GuineaPig(db.Model):  # pylint: disable=too-few-public-methods
    """
    Guinea pig model to keep track of food and weight for each
    """

    __tablename__ = "guinea_pig"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    food_entries = db.relationship("FoodEntry", secondary=food_entries)
    weight_entries = db.relationship("WeightEntry")


class FoodType(db.Model):  # pylint: disable=too-few-public-methods
    """
    Type of food to be used with the entry (and recommendations on it)
    """

    __tablename__ = "food_type"
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(64), nullable=False)
    recommendations = db.Column(db.String(512))
    entries = db.relationship("FoodEntry")
    in_statistics = db.Column(
        db.Boolean, nullable=False, default=True, info={"label": "show in statistics"}
    )
    is_hidden = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
        info={"label": "hide in food entry list"},
    )


class Entry:
    """
    Entry base class that defines a user_id foreign key and timestamp
    """

    utc_date = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def get_in_time_range(cls, start=None, end=None):
        """
        returns entries in time range or an empty list if time range
        is not specified
        """
        if not (start or end):
            return []

        query = db.session.query(cls).order_by(  # pylint: disable=no-member
            cls.utc_date
        )

        if start:
            query = query.filter(cls.utc_date >= start)

        if end:
            query = query.filter(cls.utc_date < end)

        return query.all()

    @declared_attr
    def user_id(self):
        """
        adds user foreign key to entry table
        """
        return db.Column(db.Integer, db.ForeignKey("user.id"))

    @declared_attr
    def user(self):
        """
        establishes relationship between entries and users
        """
        return db.relationship("User")


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

    @classmethod
    def get_statistics(cls):
        """
            returns statistics (most and least frequest foods and most and least recent foods)
            returns dict {stat_type: stat_value}
        """
        statistics = {}
        count_query = (
            db.session.query(  # pylint: disable=no-member
                FoodEntry.food_type_id, FoodType.label
            )
            .outerjoin(FoodEntry)
            .filter(FoodType.in_statistics == True, FoodType.is_hidden == False)   # pylint: disable=singleton-comparison
            .subquery()
        )

        food_count = db.session.query(  # pylint: disable=no-member
            count_query.c.label,
            db.func.count(count_query.c.food_type_id).label( # pylint: disable=no-member
                "count"
            ),
        ).group_by(count_query.c.label)

        latest_query = (  # pylint: disable=no-member
            db.session.query(  # pylint: disable=no-member
                FoodType.label,
                db.func.max(FoodEntry.utc_date).label(  # pylint: disable=no-member
                    "max"
                ),
            )
            .join(FoodType)
            .filter(FoodType.in_statistics == True, FoodType.is_hidden == False) # pylint: disable=singleton-comparison
            .group_by(FoodType.label)
        )

        if least_frequent := food_count.order_by(db.text("count")).first():
            statistics["least frequent"] = least_frequent[0]

        if most_frequent := food_count.order_by(db.desc(db.text("count"))).first():
            statistics["most frequent"] = most_frequent[0]

        if oldest := latest_query.order_by(db.text("max")).first():
            statistics["oldest"] = oldest[0]

        if latest := latest_query.order_by(db.desc(db.text("max"))).first():
            statistics["latest"] = latest[0]

        return statistics


class VitaminCEntry(db.Model, Entry):
    """
    Vitamin C entries only have users and timestamps
    """

    __tablename__ = "vitamin_c_entry"
    id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_today(cls):
        """
        returns vitamin C entry for today if found
        """
        return VitaminCEntry.query.filter(
            VitaminCEntry.utc_date >= beginning_of_day_utc()
        ).first()

    @classmethod
    def delete_today(cls):
        """
        deletes and returns vitamin C entry for today if found
        """
        return VitaminCEntry.query.filter(
            VitaminCEntry.utc_date >= beginning_of_day_utc()
        ).delete()


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
    guinea_pig = db.relationship("GuineaPig")

    @classmethod
    def get_most_recent(cls):
        """
        returns most recent weight or none for each guineapig [(GuineaPig.name, weight)]
        """
        return (
            db.session.query( # pylint: disable=no-member
                GuineaPig.name, WeightEntry.value
            )
            .outerjoin(WeightEntry)
            .distinct(GuineaPig.name)
            .order_by(GuineaPig.name, WeightEntry.utc_date.desc())
        )
