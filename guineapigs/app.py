from datetime import datetime
import os
from flask import Flask, render_template, redirect, request
from pytz import timezone
from guineapigs.database import Database

TIMEZONE = timezone(os.environ["TIMEZONE"])
TITLE = os.environ["TITLE"]

def init_flask():
    global app, database
    app = Flask(__name__)
    database = Database(os.environ["MONGODB_URL"])

init_flask()

@app.route("/")
def index():
    foods = database.get_foods(datetime.now(TIMEZONE).replace(hour=0, minute=0, second=0, microsecond=0))
    return render_template(
        "index.html",
        foods=foods,
        title=TITLE
        )

@app.route("/submit", methods=["POST"])
def submit():
    form = request.form
    food = {
        "name": form["name"],
        "quantity": int(form["quantity"]),
        "unit": form["unit"],
        "time": datetime.now(TIMEZONE)
    }
    database.add_food(food)
    return redirect("/")

@app.route("/vitaminc")
def vitaminc():
    food = {
        "name": "Vitamin C",
        "quantity": 1,
        "unit": "pcs",
        "time": datetime.now(TIMEZONE)
    }
    database.add_food(food)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    _id = request.form["id"]
    database.delete_food(_id)
    return redirect("/")