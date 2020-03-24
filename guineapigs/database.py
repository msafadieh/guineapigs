from bson.objectid import ObjectId
from pymongo import MongoClient

class Database:

    def __init__(self, host):
        self.client = MongoClient(host)
        self.db = self.client["guineapigs"]    
        self.foods = self.db["foods"]

    def add_food(self, food):
        self.foods.insert_one(food)

    def get_foods(self, time):
        return self.foods.find({"time": {"$gt": time}})

    def delete_food(self, _id):
        self.foods.delete_one({"_id": ObjectId(_id)})