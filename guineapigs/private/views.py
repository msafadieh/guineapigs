"""
    web routes for logged in user
"""
import heapq
from flask import (
    Blueprint,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, logout_user
from guineapigs import models
from guineapigs.extensions import db
from guineapigs.private import forms
from guineapigs.utils import (
    beginning_of_day_utc,
    beginning_of_week_utc,
    date_to_datetime,
    next_day,
)

blueprint = Blueprint("private", __name__, static_folder="../static")


@blueprint.route("/logout")
@login_required
def logout_view():
    """
    logs user out and redirects them to home
    """
    logout_user()
    return redirect(url_for("public.login"))


@blueprint.route("/")
@login_required
def dashboard():
    """
    displays dashboard with vitamin c info, today's food entries and stats,
    and guinea pig weights
    """
    return render_template(
        "dashboard.html",
        food_entries=models.FoodEntry.get_in_time_range(beginning_of_day_utc()),
        vitamin_c=models.VitaminCEntry.get_today(),
    )


@blueprint.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """
    displays history of all entries
    """
    today = beginning_of_day_utc()
    beginning_of_week = beginning_of_week_utc()
    form = forms.HistoryForm(request.form)

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
        food_entries = models.FoodEntry.get_in_time_range(start, end)
        weight_entries = models.WeightEntry.get_in_time_range(start, end)
        vitamin_c_entries = models.VitaminCEntry.get_in_time_range(start, end)

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
            (w.utc_date, "⚖️", w.value, w.guinea_pig.name, w.user.name,)
            for w in weight_entries
        )
        vitamin_c_entries = (
            (v.utc_date, "🌻", "", "", v.user.name,) for v in vitamin_c_entries
        )
        entries = heapq.merge(food_entries, weight_entries, vitamin_c_entries)

    return render_template("history.html", form=form, entries=entries)


@blueprint.route("/statistics")
@login_required
def statistics():
    """
    displays statistics page with weight info and food stats
    """
    return render_template(
        "statistics.html",
        status=models.FoodEntry.get_statistics(),
        weights=models.WeightEntry.get_most_recent(),
    )


@blueprint.route("/settings")
@login_required
def settings():
    """
    displays settings page to edit guinea pigs and food types
    """
    return render_template(
        "settings.html",
        food_types=models.FoodType.query.order_by("label").all(),
        guinea_pigs=models.GuineaPig.query.order_by(models.GuineaPig.name).all(),
    )


@blueprint.route("/vitaminc")
@login_required
def vitaminc():
    """
    adds vitaminc entry if it doesn't exist already
    """
    if models.VitaminCEntry.get_today():
        models.VitaminCEntry.delete_today()
    else:
        entry = models.VitaminCEntry()
        entry.user = current_user
        db.session.add(entry)
    db.session.commit()
    return redirect(url_for("private.dashboard"))


@blueprint.route("/food_entry/delete", methods=["POST"])
@login_required
def delete_food_entry():
    """
    deletes FoodEntry row and clears its relationship
    with guinea pigs
    """
    if food_entry_id := request.form.get("id"):
        if food_entry_id.isdecimal():
            entry = models.FoodEntry.query.filter(
                models.FoodEntry.id == int(food_entry_id)
            )
            entry.first().guinea_pigs = []
            entry.delete()
            db.session.commit()
    return redirect(url_for("private.dashboard"))


@blueprint.route("/food_entry/add", methods=["GET", "POST"])
@blueprint.route("/food_entry/edit/<int:id_>", methods=["GET", "POST"])
@login_required
def food_entry_form(id_=None):
    """
    inserts/edits a food entry
    """
    form = forms.FoodEntryForm()
    form.food_type_id.choices = [
        (food_entry.id, food_entry.label)
        for food_entry in models.FoodType.query.order_by(models.FoodType.label)
        .filter(models.FoodType.is_hidden == False) # pylint: disable=singleton-comparison
        .all()
    ]
    form.guinea_pig_ids.choices = [
        (guinea_pig.id, guinea_pig.name)
        for guinea_pig in models.GuineaPig.query.order_by(models.GuineaPig.name).all()
    ]

    entry = None
    if id_:
        entry = models.FoodEntry.query.filter(models.FoodEntry.id == id_).first()

    if form.validate_on_submit():

        entry = entry or models.FoodEntry()
        entry.food_type_id = form.food_type_id.data
        entry.notes = form.notes.data
        entry.user = current_user
        entry.guinea_pigs = models.GuineaPig.query.filter(
            models.GuineaPig.id.in_(form.guinea_pig_ids.data)
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


@blueprint.route("/weight_entry/add", methods=["GET", "POST"])
@blueprint.route("/weight_entry/edit/<int:id_>", methods=["GET", "POST"])
@login_required
def weight_entry_form(id_=None):
    """
    insert/edit a weight entry
    """
    form = forms.WeightEntryForm()
    form.guinea_pig_id.choices = [
        (guinea_pig.id, guinea_pig.name)
        for guinea_pig in models.GuineaPig.query.order_by(models.GuineaPig.name).all()
    ]

    entry = None
    if id_:
        entry = models.WeightEntry.query.filter(models.WeightEntry.id == id_).first()

    if form.validate_on_submit():
        entry = entry or models.WeightEntry()
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


@blueprint.route("/guinea_pig/add", methods=["GET", "POST"])
@blueprint.route("/guinea_pig/edit/<int:id>", methods=["GET", "POST"])
@login_required
def guinea_pig_form(id_=None):
    """
    insert/edit guinea pigs
    """
    form = forms.GuineaPigForm()
    guinea_pig = None
    if id_:
        guinea_pig = models.GuineaPig.query.filter(models.GuineaPig.id == id_).first()

    if form.validate_on_submit():
        guinea_pig = guinea_pig or models.GuineaPig()
        guinea_pig.name = form.name.data
        db.session.add(guinea_pig)
        db.session.commit()
        return jsonify(status="ok")

    if guinea_pig:
        form.name.data = guinea_pig.name

    return render_template("forms/guinea_pig_form.html", guinea_pig_form=form)


@blueprint.route("/food_type/add", methods=["GET", "POST"])
@blueprint.route("/food_type/edit/<int:id_>", methods=["GET", "POST"])
@login_required
def food_type_form(id_=None):
    """
    insert/edit guinea pigs
    """
    form = forms.FoodTypeForm()
    food_entry = None

    if id__:
        food_entry = models.FoodType.query.filter(models.FoodType.id == id__).first()

    if form.validate_on_submit():
        food_entry = food_entry or models.FoodType()
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
