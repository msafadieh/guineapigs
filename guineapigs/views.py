from flask import redirect, render_template, request
from flask_login import current_user, login_required, login_user
from guineapigs.app import app, db
from guineapigs.forms import *
from guineapigs.models import *

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate():
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
    return render_template("dashboard.html",
            add_food_entry=FoodEntryForm(),
            add_weight_entry=WeightEntryForm(),
            food_entries=FoodEntry.get_entries_from_today().all(),
            vitamin_c=VitaminCEntry.get_entries_from_today().first())


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html",
            add_food_type=FoodTypeForm(),
            add_guinea_pig=GuineaPigForm(),
            food_types=list(FoodType.query.sort_by("label").all()),
            guinea_pigs=list(GuineaPig.query.sort_by("name").all()))

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
    form.food_type_id.choices = [(ft.id, ft.label) for ft in FoodType.query.sort_by("name").all()]
    form.guinea_pig_ids.choices = [(gp.id, gp.name) for gp in GuineaPig.query.sort_by("name").all()]

    if form.validate_on_submit():
        entry = FoodEntry()
        entry.food_type_id = FoodType.query.filter(FoodType.id==int(form.food_type_id.data)).first()
        entry.notes = form.notes.data
        entry.guinea_pigs = GuineaPig.query.filter(GuineaPig.id.in_(form.guinea_pig_ids.data))
        db.session.add(entry)
        db.session.commit()
        return jsonify(status=ok)

    return render_template("forms/add_food_entry.html", add_food_entry_form=form)


@app.route("/weight_entry/add", methods=["POST"])
@login_required
def add_weight_entry():
    form = WeightEntryForm()
    form.guinea_pig_ids.choices = [(gp.id, gp.name) for gp in GuineaPig.query.sort_by("name").all()]

    if form.validate_on_submit():
        entry = FoodEntry()
        entry.value = float(form.value.data)
        entry.guinea_pig_id = GuineaPig.query.filter(GuineaPig.id==form.guinea_pig_ids.data).first()
        db.session.add(entry)
        db.session.commit()
        return jsonify(status=ok)

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
        return jsonify(status=ok)

    return render_template("forms/add_weight_entry.html", add_guinea_pig=form)

@app.route("/food_type/add", methods=["POST"])
@login_required
def add_food_type():
    form = FoodTypeForm()

    if form.validate_on_submit():
        ft.label = form.label.data
        ft.recommendations = form.recommendations.data
        ft.save()
        return jsonify(status=ok)

    return render_template("forms/add_food_type.html", add_food_type=form)

