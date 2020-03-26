from datetime import datetime
from functools import wraps
import os
import random
from flask import Flask, make_response, render_template, redirect, request
from guineapigs.database import Database

TITLE = os.environ["TITLE"]

QUOTES = [
    ("a karot a day keps the squekz awey", "stella"),
    ("best wey 4 food? snetch it and run before humen catches u", "luna")
]

FOOD_OPTIONS = [
    "Carrot",
    "Kale",
    "Lettuce",
    "Pea flake",
    "Spinach",
    "Treats"
]

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
    return render("index.html",
                  foods=database.get_foods(),
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
        if (qnt := form.get("quantity", "")).replace(".", "", 1).isdecimal():
            database.add_food(name, float(qnt), request.cookies["name"])
    return redirect("/")

@app.route("/vitaminc")
@check_cookie
def vitaminc():
    database.add_food("Vitamin C", 1.0, request.cookies["name"])
    return redirect("/")

@app.route("/delete", methods=["POST"])
@check_cookie
def delete():
    database.delete_food(request.form["id"])
    return redirect("/")
