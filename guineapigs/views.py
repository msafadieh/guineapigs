from flask import jsonify, redirect, render_template, request
from flask_login import current_user, login_required, login_user
from guineapigs.app import app, db
from guineapigs.forms import *
from guineapigs.models import *
from guineapigs.utils import beginning_of_day_utc

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if not (user := User.query.filter(User.name==form.name.data).first()):
            user = User()
            user.name = form.name.data
            db.session.add(user)
            db.session.commit()

        login_user(user)

        return redirect("/")
    
    print(form.errors.items())
    return render_template("login.html", login_form=form)

@app.route("/")
@login_required
def dashboard():
    vitamin_c = (db.session.query(VitaminCEntry.utc_date, User.name)
                              .filter(VitaminCEntry.utc_date >= beginning_of_day_utc())
                              .first()
                )
    
    food_entries = (db.session.query(FoodType.label, FoodEntry, User.name)
                              .filter(FoodEntry.utc_date >= beginning_of_day_utc())
                              .order_by(FoodEntry.utc_date)
                              .all()
                   )

    weights = (db.session.query(GuineaPig.name, WeightEntry.value)
                         .outerjoin(WeightEntry)
                         .distinct(GuineaPig.name)
                         .order_by(GuineaPig.name, WeightEntry.utc_date.desc()))

    add_food_entry = FoodEntryForm()
    add_food_entry.food_type_id.choices = [(ft.id, ft.label) for ft in FoodType.query.order_by(FoodType.label).all()]
    add_food_entry.guinea_pig_ids.choices = [(gp.id, gp.name) for gp in GuineaPig.query.order_by(GuineaPig.name).all()]

    add_weight_entry = WeightEntryForm()
    add_weight_entry.guinea_pig_id.choices = [(gp.id, gp.name) for gp in GuineaPig.query.order_by(GuineaPig.name).all()]

    return render_template("dashboard.html",
            add_food_entry=add_food_entry,
            add_weight_entry=add_weight_entry,
            food_entries=food_entries,
            weights=weights,
            vitamin_c=vitamin_c)


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html",
            add_food_type=FoodTypeForm(),
            add_guinea_pig=GuineaPigForm(),
            food_types=FoodType.query.order_by("label").all(),
            guinea_pigs=GuineaPig.query.order_by(GuineaPig.name).all())

@app.route("/vitaminc")
@login_required
def vitaminc():
    if not VitaminCEntry.get_entries_from_today().first():
        entry = VitaminCEntry()
        entry.user = current_user.id
        db.session.add(entry)
        db.session.commit()
    return redirect("/")

@app.route("/food_entry/add", methods=["POST"])
@login_required
def add_food_entry():
    form = FoodEntryForm()
    form.food_type_id.choices = [(ft.id, ft.label) for ft in FoodType.query.order_by(FoodType.label).all()]
    form.guinea_pig_ids.choices = [(gp.id, gp.name) for gp in GuineaPig.query.order_by(GuineaPig.name).all()]

    if form.validate_on_submit():
        entry = FoodEntry()
        entry.food_type_id = form.food_type_id.data
        entry.notes = form.notes.data
        entry.guinea_pigs = GuineaPig.query.filter(GuineaPig.id.in_(form.guinea_pig_ids.data)).all()
        db.session.add(entry)
        db.session.commit()
        return jsonify(status='ok')

    return render_template("forms/add_food_entry.html", add_food_entry_form=form)


@app.route("/weight_entry/add", methods=["POST"])
@login_required
def add_weight_entry():
    form = WeightEntryForm()
    form.guinea_pig_id.choices = [(gp.id, gp.name) for gp in GuineaPig.query.order_by(GuineaPig.name).all()]

    if form.validate_on_submit():
        entry = WeightEntry()
        entry.value = float(form.value.data)
        entry.guinea_pig_id = form.guinea_pig_id.data
        db.session.add(entry)
        db.session.commit()
        return jsonify(status='ok')

    return render_template("forms/add_weight_entry.html", add_weight_entry=form)


@app.route("/guinea_pig/add", methods=["POST"])
@login_required
def add_guinea_pig():
    form = GuineaPigForm()

    if form.validate_on_submit():
        gp = GuineaPig()
        gp.name = form.name.data
        db.session.add(gp)
        db.session.commit()
        return jsonify(status='ok')

    return render_template("forms/add_weight_entry.html", add_guinea_pig=form)

@app.route("/food_type/add", methods=["POST"])
@login_required
def add_food_type():
    form = FoodTypeForm()

    if form.validate_on_submit():
        ft = FoodType()
        ft.label = form.label.data
        ft.recommendations = form.recommendations.data
        db.session.add(ft)
        db.session.commit()
        return jsonify(status='ok')

    return render_template("forms/add_food_type.html", add_food_type=form)

