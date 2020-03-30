from datetime import datetime
from functools import wraps
import os
import random
from flask import Flask, make_response, render_template, redirect, request
from guineapigs.database import Database
from guineapigs.utils import split_dates, start_of_day_and_week

TITLE = os.environ["TITLE"]

QUOTES = [
    ("a karot a day keps the squekz awey", "stella"),
    ("best wey 4 food? snetch it and run before humen catches u", "luna")
]

FOOD_OPTIONS = """banana 🍌
carrot 🥕
cucumber 🥒
green pepper 🔔
kale 🥬
pea flake 🥣
red leaf lettuce 🥬
romaine Lettuce 🥬
spinach 🥬
tomato 🍅
treats 🍬""".split("\n")

def init_flask():
    global app, database
    app = Flask(__name__)
    database = Database()

init_flask()

def check_cookie(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        if request.cookies.get("name"):
            return func(*args, **kwargs)
        return redirect("/setname")
    return wrapped

def render(*args, **kwargs):
    return render_template(
        *args,
        title=TITLE,
        quote=random.choice(QUOTES),
        **kwargs
    )

@app.route("/")
@check_cookie
def index():
    older = bool(request.args.get("older"))
    start_day, start_week = start_of_day_and_week(os.environ["TIMEZONE"])
    
    foods = database.get_foods(start_week if older else start_day)
    foods = split_dates(foods)
    
    if foods:
        date, entries = foods.popitem(last=False)
        key = "today" if entries[0]["time"] >= start_day else date
        foods[key] = entries
        foods.move_to_end(key, last=False)

    return render("index.html",
                  entries=foods,
                  food_options=FOOD_OPTIONS)

@app.route("/setname", methods=["GET", "POST"])
def set_name():
    saved_name = request.cookies.get("name")

    if saved_name:
        return redirect("/")

    if request.method == "POST" and (name := request.form.get("name")):
        resp = make_response(redirect("/"))
        resp.set_cookie("name", name)
        return resp

    return render("setname.html")

@app.route("/removename")
@check_cookie
def remove_name():
    resp = make_response(redirect("/setname"))
    resp.set_cookie("name", "")
    return resp

@app.route("/submit", methods=["POST"])
@check_cookie
def submit():
    form = request.form
    if (name := form.get("name")) in FOOD_OPTIONS:
        database.add_food(name, form.get("notes", ""), request.cookies["name"])
    return redirect("/")

@app.route("/vitaminc")
@check_cookie
def vitaminc():
    database.add_food("vitamin c 🌻", "", request.cookies["name"])
    if request.args.get("older"):
        return redirect("/?older=1")
    return redirect("/")

@app.route("/delete", methods=["POST"])
@check_cookie
def delete():
    database.delete_food(request.form["id"])
    if request.form.get("older"):
        return redirect("/?older=1")
    return redirect("/")
