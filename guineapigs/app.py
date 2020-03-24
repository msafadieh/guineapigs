from datetime import datetime
import os
from flask import Flask, render_template, redirect, request
from guineapigs.database import Database

TITLE = os.environ["TITLE"]
UNITS = [
    "g",
    "oz",
    "pcs"
]

def init_flask():
    global app, database
    app = Flask(__name__)
    database = Database()

init_flask()

@app.route("/")
def index():
    return render_template(
        "index.html",
        foods=database.get_foods(),
        title=TITLE,
        units=UNITS
        )

@app.route("/submit", methods=["POST"])
def submit():
    database.add_food(request.form["name"],
                      request.int(form["quantity"]),
                      request.form["unit"])
    return redirect("/")

@app.route("/vitaminc")
def vitaminc():
    database.add_food("Vitamin C", 1, "pcs")
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    database.delete_food(request.form["id"])
    return redirect("/")