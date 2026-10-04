"""Authentication routes: register, login, logout."""
import re
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session,
)
from werkzeug.security import generate_password_hash, check_password_hash

from db import query, execute
from helpers import current_user

bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user():
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        errors = []
        if len(name) < 2:
            errors.append("Please enter your name.")
        if not EMAIL_RE.match(email):
            errors.append("Please enter a valid email address.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")
        if password != confirm:
            errors.append("Passwords do not match.")
        if query("SELECT id FROM users WHERE email = ?", (email,), one=True):
            errors.append("An account with this email already exists.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("register.html", name=name, email=email)

        uid = execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?,?,?)",
            (name, email, generate_password_hash(password)),
        )
        session["user_id"] = uid
        flash(f"Welcome to Quickbyte, {name}!", "success")
        return redirect(url_for("main.index"))

    return render_template("register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user():
        return redirect(url_for("main.index"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        nxt = request.form.get("next") or request.args.get("next")

        user = query("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['name']}!", "success")
            # Only allow local redirects (open-redirect protection)
            if nxt and nxt.startswith("/"):
                return redirect(nxt)
            return redirect(url_for("main.index"))
        flash("Invalid email or password.", "error")
        return render_template("login.html", email=email, next=nxt)

    return render_template("login.html", next=request.args.get("next"))


@bp.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    flash("You have been logged out.", "success")
    return redirect(url_for("main.index"))
