from flask import jsonify, redirect, render_template, request
from flask_login import current_user, login_required, login_user, logout_user
from pytz import utc
from guineapigs.app import app, db
from guineapigs.forms import *
from guineapigs.models import *
from guineapigs.utils import beginning_of_day_utc

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name = form.name.data.lower().split(' ')[0]
        if not (user := User.query.filter(User.name==name).first()):
            user = User()
            user.name = name
            db.session.add(user)
            db.session.commit()

        login_user(user)

        return redirect("/")
    
    return render_template("login.html", login_form=form)

@app.route("/logout")
def logout_view():
    logout_user()
    return redirect("/")

@app.route("/")
@login_required
def dashboard():
    begin_of_day = beginning_of_day_utc()
    vitamin_c = (db.session.query(VitaminCEntry.utc_date, User.name)
                              .filter(VitaminCEntry.utc_date >= begin_of_day)
                              .first())
    
    food_entries = (db.session.query(FoodEntry)
                              .filter(FoodEntry.utc_date >= begin_of_day)
                              .order_by(FoodEntry.utc_date)
                              .all())

    weights = (db.session.query(GuineaPig.name, WeightEntry.value)
                         .outerjoin(WeightEntry)
                         .distinct(GuineaPig.name)
                         .order_by(GuineaPig.name, WeightEntry.utc_date.desc()))

    subq = (db.session.query(FoodEntry.food_type_id, db.func.count(FoodEntry.food_type_id).label('count'))
                                 .group_by(FoodEntry.food_type_id)
                                 .subquery())
    food_count = db.session.query(FoodType.label, subq.c.count).join(subq, subq.c.food_type_id == FoodType.id).all()
    food_latest = (db.session.query(FoodType.label, FoodEntry.utc_date)
                            .outerjoin(FoodEntry)
                            .distinct(FoodType.label)
                            .order_by(FoodType.label, FoodEntry.utc_date.desc()))
    status = {}
    status["latest"] = max(food_latest, key=lambda f: f[1])[0]
    status["oldest"] = min(food_latest, key=lambda f: f[1])[0]
    status["most frequent"] = max(food_count, key=lambda f: f[1])[0]
    status["least frequent"] = min(food_count, key=lambda f: f[1])[0]

    return render_template("dashboard.html",
            food_entries=food_entries,
            weights=weights,
            utc=utc,
            vitamin_c=vitamin_c,
            status=status)


@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html",
            food_types=FoodType.query.order_by("label").all(),
            guinea_pigs=GuineaPig.query.order_by(GuineaPig.name).all())

@app.route("/vitaminc")
@login_required
def vitaminc():
    if not VitaminCEntry.get_entries_from_today().first():
        entry = VitaminCEntry()
        entry.user = current_user
        db.session.add(entry)
        db.session.commit()
    return redirect("/")

@app.route("/food_entry/delete", methods=["POST"])
@login_required
def delete_food_entry():
    if (food_entry_id := request.form.get("id")) and food_entry_id.isdecimal():
        FoodEntry.query.filter(FoodEntry.id == int(food_entry_id)).delete()
        db.session.commit()
    return redirect("/")

@app.route("/food_entry/add", methods=["GET", "POST"])
@app.route("/food_entry/edit/<int:id>", methods=["GET", "POST"])
@login_required
def add_food_entry(id=None):
    form = FoodEntryForm()
    form.food_type_id.choices = [(ft.id, ft.label) for ft in FoodType.query.order_by(FoodType.label).all()]
    form.guinea_pig_ids.choices = [(gp.id, gp.name) for gp in GuineaPig.query.order_by(GuineaPig.name).all()]

    entry = None
    if id:
        entry = FoodEntry.query.filter(FoodEntry.id==id).first()

    if form.validate_on_submit():

        entry = entry or FoodEntry()
        entry.food_type_id = form.food_type_id.data
        entry.notes = form.notes.data
        entry.user = current_user
        entry.guinea_pigs = GuineaPig.query.filter(GuineaPig.id.in_(form.guinea_pig_ids.data)).all()
        db.session.add(entry)
        db.session.commit()
        return jsonify(status='ok')

    if entry:
        form.food_type_id.data = entry.food_type_id 
        form.notes.data = entry.notes
        form.guinea_pigs_ids.data = [gp.id for gp in entry.guinea_pigs]

    return render_template("forms/add_food_entry.html", add_food_entry=form)


@app.route("/weight_entry/add", methods=["GET", "POST"])
@app.route("/weight_entry/edit/<int:id>", methods=["GET", "POST"])
@login_required
def add_weight_entry(id=None):
    form = WeightEntryForm()
    form.guinea_pig_id.choices = [(gp.id, gp.name) for gp in GuineaPig.query.order_by(GuineaPig.name).all()]
    
    entry = None
    if id:
        entry = WeightEntry.query.filter(WeightEntry.id==id).first()

    if form.validate_on_submit():
        entry = entry or WeightEntry()
        entry.value = float(form.value.data)
        entry.guinea_pig_id = form.guinea_pig_id.data
        entry.user = current_user
        db.session.add(entry)
        db.session.commit()
        return jsonify(status='ok')
    
    if entry:
        form.value.data = entry.value
        form.guinea_pig_id.data = entry.guinea_pig_id

    return render_template("forms/add_weight_entry.html", add_weight_entry=form)


@app.route("/guinea_pig/add", methods=["GET", "POST"])
@app.route("/guinea_pig/edit/<int:id>", methods=["GET", "POST"])
@login_required
def add_guinea_pig(id=None):
    form = GuineaPigForm()
    gp = None
    if id:
        gp = GuineaPig.query.filter(GuineaPig.id==id).first()

    if form.validate_on_submit():
        gp = gp or GuineaPig()
        gp.name = form.name.data
        db.session.add(gp)
        db.session.commit()
        return jsonify(status='ok')
    
    if gp:
        form.name.data = gp.name

    return render_template("forms/add_guinea_pig.html", add_guinea_pig=form)

@app.route("/food_type/add", methods=["GET", "POST"])
@app.route("/food_type/edit/<int:id>", methods=["GET", "POST"])
@login_required
def add_food_type(id=None):
    form = FoodTypeForm()
    ft = None

    if id:
        ft = FoodType.query.filter(FoodType.id==id).first()

    if form.validate_on_submit():
        ft = ft or FoodType()
        ft.label = form.label.data
        ft.recommendations = form.recommendations.data
        db.session.add(ft)
        db.session.commit()
        return jsonify(status='ok')
        
    if ft:
        form.label.data = ft.label
        form.recommendations.data = ft.recommendations

    return render_template("forms/add_food_type.html", add_food_type=form)

