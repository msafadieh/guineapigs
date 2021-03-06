"""
    web routes for logged out users
"""
from flask import abort, Blueprint, render_template, redirect, request, url_for
from flask_login import current_user, login_user
from guineapigs.models import User
from guineapigs.extensions import db, login_manager
from guineapigs.utils import is_safe_url
from guineapigs.public.forms import LoginForm

blueprint = Blueprint("public", __name__, static_folder="../static")

login_manager.login_view = "public.login"


@login_manager.user_loader
def user_loader(user_id):
    """
    Locates user in database using its id
    """
    return User.query.filter(User.id == user_id).first()


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    """
    displays login form and logins user in
    """
    form = LoginForm(request.form)
    if request.method == "POST" and form.validate():
        name = form.name.data.lower().split(" ")[0]
        user = User.query.filter(User.name == name).first()
        if not user:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()

        login_user(user, remember=True)

    if next_ := request.args.get("next"):
        if not is_safe_url(next_, request.host_url):
            return abort(400)

    if current_user.is_authenticated:
        return redirect(next_ or url_for("private.dashboard"))
    return render_template("login.html", login_form=form)
