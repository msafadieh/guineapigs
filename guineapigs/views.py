"""
    web routes
"""
import heapq
from flask import abort, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from pytz import utc
from guineapigs.app import app, db
from guineapigs.forms import *
from guineapigs.models import *
from guineapigs.utils import (
    beginning_of_day_utc,
    beginning_of_week_utc,
    date_to_datetime,
    is_safe_url,
    next_day,
)


@app.context_processor
def variables():
    return {
        "NAV_PAGES": NAV_PAGES_LOGGED_IN
        if current_user.is_authenticated
        else NAV_PAGES_LOGGED_OUT,

        "UTC": utc
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    displays login form and logins user in
    """
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data.lower().split(" ")[0]
        if not (user := User.query.filter(User.name == name).first()):
            user = User()
            user.name = name
            db.session.add(user)
            db.session.commit()

        login_user(user, remember=True)

    if (next_ := request.args.get("next")) and not is_safe_url(next_, request.host_url):
        return abort(400)

    if current_user.is_authenticated:
        return redirect(next_ or url_for("dashboard"))
    return render_template("login.html", login_form=form)


@app.route("/logout")
def logout_view():
    """
    logs user out and redirects them to home
    """
    logout_user()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def dashboard():
    """
    displays dashboard with vitamin c info, today's food entries and stats,
    and guinea pig weights
    """
    food_entries = (
        db.session.query(FoodEntry)
        .filter(FoodEntry.utc_date >= beginning_of_day_utc())
        .order_by(FoodEntry.utc_date.desc())
    )

    return render_template(
        "dashboard.html",
        food_entries=food_entries,
        utc=utc,
        vitamin_c=VitaminCEntry.get_today(),
    )


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """
    displays history of all entries
    """
    today = beginning_of_day_utc()
    beginning_of_week = beginning_of_week_utc()
    form = HistoryForm(request.form)

    start = end = None

    if request.method == "GET":
        start = beginning_of_week
        end = today
        form.start.data = beginning_of_week.date()
        form.end.data = today.date()
    elif form.validate():
        start = date_to_datetime(form.start.data)
        end = date_to_datetime(form.end.data)

    entries = []
    if start and end:
        end = next_day(end)
        food_entries = FoodEntry.get_in_time_range(start, end)
        weight_entries = WeightEntry.get_in_time_range(start, end)
        vitamin_c_entries = VitaminCEntry.get_in_time_range(start, end)

        food_entries = (
            (
                f.utc_date,
                "🍽️",
                f.food_type.label,
                ", ".join(gp.name for gp in f.guinea_pigs),
                f.user.name,
            )
            for f in food_entries
        )
        weight_entries = (
            (
                w.utc_date,
                "⚖️",
                w.value,
                w.guinea_pig.name,
                w.user.name,
            )
            for w in weight_entries
        )
        vitamin_c_entries = (
            (v.utc_date, "🌻", "", "", v.user.name,)
            for v in vitamin_c_entries
        )
        entries = heapq.merge(food_entries, weight_entries, vitamin_c_entries)

    return render_template("history.html", form=form, entries=entries)


@app.route("/statistics")
@login_required
def statistics():
    """
    displays statistics page with weight info and food stats
    """
    subq = (
        db.session.query(
            FoodEntry.food_type_id, db.func.count(FoodEntry.food_type_id).label("count")
        )
        .group_by(FoodEntry.food_type_id)
        .subquery()
    )

    weights = (
        db.session.query(GuineaPig.name, WeightEntry.value)
        .outerjoin(WeightEntry)
        .distinct(GuineaPig.name)
        .order_by(GuineaPig.name, WeightEntry.utc_date.desc())
    )

    food_count = (
        db.session.query(FoodType.label, subq.c.count)
        .outerjoin(subq, subq.c.food_type_id == FoodType.id)
        .filter(FoodType.in_statistics == True)
        .filter(FoodType.is_hidden == False)
        .all()
    )
    food_latest = (
        db.session.query(FoodType.label, FoodEntry.utc_date)
        .join(FoodEntry)
        .distinct(FoodType.label)
        .filter(FoodType.in_statistics == True)
        .filter(FoodType.is_hidden == False)
        .order_by(FoodType.label, FoodEntry.utc_date.desc())
    )
    status = {}
    food_count = [(label, count or 0) for label, count in food_count]
    if food_count:
        status["latest"] = max(food_latest, key=lambda f: f[1])[0]
        status["oldest"] = min(food_latest, key=lambda f: f[1])[0]
        status["most frequent"] = max(food_count, key=lambda f: f[1])[0]
        status["least frequent"] = min(food_count, key=lambda f: f[1])[0]
    return render_template("statistics.html", status=status, weights=weights)


@app.route("/settings")
@login_required
def settings():
    """
    displays settings page to edit guinea pigs and food types
    """
    return render_template(
        "settings.html",
        food_types=FoodType.query.order_by("label").all(),
        guinea_pigs=GuineaPig.query.order_by(GuineaPig.name).all(),
    )


@app.route("/vitaminc")
@login_required
def vitaminc():
    """
    adds vitaminc entry if it doesn't exist already
    """
    if VitaminCEntry.get_today():
        VitaminCEntry.delete_today()
    else:
        entry = VitaminCEntry()
        entry.user = current_user
        db.session.add(entry)
    db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/food_entry/delete", methods=["POST"])
@login_required
def delete_food_entry():
    """
    deletes FoodEntry row and clears its relationship
    with guinea pigs
    """
    if (food_entry_id := request.form.get("id")) and food_entry_id.isdecimal():
        entry = FoodEntry.query.filter(FoodEntry.id == int(food_entry_id))
        entry.first().guinea_pigs = []
        entry.delete()
        db.session.commit()
    return redirect(url_for("dashboard"))


@app.route("/food_entry/add", methods=["GET", "POST"])
@app.route("/food_entry/edit/<int:id>", methods=["GET", "POST"])
@login_required
def food_entry_form(id=None):
    """
    inserts/edits a food entry
    """
    form = FoodEntryForm()
    form.food_type_id.choices = [
        (food_entry.id, food_entry.label)
        for food_entry in FoodType.query.order_by(FoodType.label)
        .filter(FoodType.is_hidden == False)
        .all()
    ]
    form.guinea_pig_ids.choices = [
        (guinea_pig.id, guinea_pig.name)
        for guinea_pig in GuineaPig.query.order_by(GuineaPig.name).all()
    ]

    entry = None
    if id:
        entry = FoodEntry.query.filter(FoodEntry.id == id).first()

    if form.validate_on_submit():

        entry = entry or FoodEntry()
        entry.food_type_id = form.food_type_id.data
        entry.notes = form.notes.data
        entry.user = current_user
        entry.guinea_pigs = GuineaPig.query.filter(
            GuineaPig.id.in_(form.guinea_pig_ids.data)
        ).all()
        db.session.add(entry)
        db.session.commit()
        return jsonify(status="ok")

    if entry:
        form.food_type_id.data = entry.food_type_id
        form.notes.data = entry.notes
        form.guinea_pig_ids.data = [guinea_pig.id for guinea_pig in entry.guinea_pig]
    else:
        form.guinea_pig_ids.data = [
            guinea_pig[0] for guinea_pig in form.guinea_pig_ids.choices
        ]

    return render_template("forms/food_entry_form.html", food_entry_form=form)


@app.route("/weight_entry/add", methods=["GET", "POST"])
@app.route("/weight_entry/edit/<int:id>", methods=["GET", "POST"])
@login_required
def weight_entry_form(id=None):
    """
    insert/edit a weight entry
    """
    form = WeightEntryForm()
    form.guinea_pig_id.choices = [
        (guinea_pig.id, guinea_pig.name)
        for guinea_pig in GuineaPig.query.order_by(GuineaPig.name).all()
    ]

    entry = None
    if id:
        entry = WeightEntry.query.filter(WeightEntry.id == id).first()

    if form.validate_on_submit():
        entry = entry or WeightEntry()
        entry.value = float(form.value.data)
        entry.guinea_pig_id = form.guinea_pig_id.data
        entry.user = current_user
        db.session.add(entry)
        db.session.commit()
        return jsonify(status="ok")

    if entry:
        form.value.data = entry.value
        form.guinea_pig_id.data = entry.guinea_pig_id

    return render_template("forms/weight_entry_form.html", weight_entry_form=form)


@app.route("/guinea_pig/add", methods=["GET", "POST"])
@app.route("/guinea_pig/edit/<int:id>", methods=["GET", "POST"])
@login_required
def guinea_pig_form(id=None):
    """
    insert/edit guinea pigs
    """
    form = GuineaPigForm()
    guinea_pig = None
    if id:
        guinea_pig = GuineaPig.query.filter(GuineaPig.id == id).first()

    if form.validate_on_submit():
        guinea_pig = guinea_pig or GuineaPig()
        guinea_pig.name = form.name.data
        db.session.add(guinea_pig)
        db.session.commit()
        return jsonify(status="ok")

    if guinea_pig:
        form.name.data = guinea_pig.name

    return render_template("forms/guinea_pig_form.html", guinea_pig_form=form)


@app.route("/food_type/add", methods=["GET", "POST"])
@app.route("/food_type/edit/<int:id_>", methods=["GET", "POST"])
@login_required
def food_type_form(id_=None):
    """
    insert/edit guinea pigs
    """
    form = FoodTypeForm()
    food_entry = None

    if id_:
        food_entry = FoodType.query.filter(FoodType.id == id_).first()

    if form.validate_on_submit():
        food_entry = food_entry or FoodType()
        food_entry.label = form.label.data
        food_entry.recommendations = form.recommendations.data
        food_entry.is_hidden = form.is_hidden.data
        food_entry.in_statistics = form.in_statistics.data
        db.session.add(food_entry)
        db.session.commit()
        return jsonify(status="ok")

    if food_entry:
        form.label.data = food_entry.label
        form.recommendations.data = food_entry.recommendations
        form.is_hidden.data = food_entry.is_hidden
        form.in_statistics.data = food_entry.in_statistics

    return render_template("forms/food_type_form.html", food_type_form=form)


NAV_PAGES_LOGGED_IN = (
    ("dashboard", "dashboard",),
    ("history", "history",),
    ("statistics", "statistics",),
    ("settings", "settings",),
    ("log out", "logout_view",),
)

NAV_PAGES_LOGGED_OUT = (("log in", "login",),)
