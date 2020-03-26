from datetime import datetime, timedelta
import os
from bson import CodecOptions
from bson.objectid import ObjectId
from pymongo import MongoClient
from pytz import timezone

class Database:

    def __init__(self):
        self.client = MongoClient(os.environ["MONGODB_URL"])
        self.db = self.client["guineapigs"]    
        self.foods = self.db["foods"]
        self.timezone = timezone(os.environ["TIMEZONE"])
        self.timezone_aware = self.foods.with_options(
            codec_options=CodecOptions(
                tz_aware=True,
                tzinfo=self.timezone
            )
        )

    def add_food(self, name, notes, person):
        food = {
            "name": name,
            "person": person,
            "notes": notes,
            "time": datetime.utcnow()
        }
        self.foods.insert_one(food)

    def get_foods(self, older):
        day_begin = datetime.now(self.timezone).replace(hour=0,
                                                        minute=0,
                                                        second=0,
                                                        microsecond=0)
        filter_ = {"time": {"$gt": day_begin - timedelta(days=6) if older else day_begin}}
        return self.timezone_aware.find(filter_).sort("time", -1)

    def delete_food(self, _id):
        self.foods.delete_one({"_id": ObjectId(_id)})