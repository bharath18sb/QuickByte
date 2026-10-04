"""Admin routes: login, dashboard, manage restaurants/food/categories/orders."""
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session,
)
from werkzeug.security import check_password_hash

from db import query, execute
from helpers import admin_required, current_user, ORDER_STATUSES

bp = Blueprint("admin", __name__, url_prefix="/admin")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
@bp.route("/login", methods=["GET", "POST"])
def login():
    user = current_user()
    if user and user["is_admin"]:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        u = query("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if u and u["is_admin"] and check_password_hash(u["password_hash"], password):
            session["user_id"] = u["id"]
            flash("Welcome to the admin panel.", "success")
            return redirect(url_for("admin.dashboard"))
        flash("Invalid admin credentials.", "error")
    return render_template("admin/login.html")


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------
@bp.route("/")
@admin_required
def dashboard():
    stats = {
        "users": query("SELECT COUNT(*) c FROM users WHERE is_admin = 0", one=True)["c"],
        "restaurants": query("SELECT COUNT(*) c FROM restaurants", one=True)["c"],
        "foods": query("SELECT COUNT(*) c FROM food_items", one=True)["c"],
        "orders": query("SELECT COUNT(*) c FROM orders", one=True)["c"],
        "revenue": query(
            "SELECT COALESCE(SUM(total),0) s FROM orders WHERE status != 'CANCELLED'",
            one=True)["s"],
    }
    recent = query(
        """SELECT o.*, u.name AS customer FROM orders o
           JOIN users u ON u.id = o.user_id
           ORDER BY o.id DESC LIMIT 8"""
    )
    return render_template("admin/dashboard.html", stats=stats, recent=recent)


# ---------------------------------------------------------------------------
# Restaurants
# ---------------------------------------------------------------------------
@bp.route("/restaurants")
@admin_required
def restaurants():
    rows = query("SELECT * FROM restaurants ORDER BY id DESC")
    return render_template("admin/restaurants.html", restaurants=rows)


@bp.route("/restaurants/new", methods=["GET", "POST"])
@bp.route("/restaurants/<int:rid>/edit", methods=["GET", "POST"])
@admin_required
def restaurant_form(rid=None):
    rest = None
    if rid:
        rest = query("SELECT * FROM restaurants WHERE id = ?", (rid,), one=True)
        if not rest:
            flash("Restaurant not found.", "error")
            return redirect(url_for("admin.restaurants"))

    if request.method == "POST":
        data = _restaurant_data()
        if not data["name"]:
            flash("Restaurant name is required.", "error")
            return render_template("admin/restaurant_form.html", rest=request.form)
        if rid:
            execute(
                """UPDATE restaurants SET name=?, cuisine=?, rating=?,
                   delivery_time=?, image=?, description=?, active=? WHERE id=?""",
                (data["name"], data["cuisine"], data["rating"],
                 data["delivery_time"], data["image"], data["description"],
                 data["active"], rid),
            )
            flash("Restaurant updated.", "success")
        else:
            execute(
                """INSERT INTO restaurants
                   (name, cuisine, rating, delivery_time, image, description, active)
                   VALUES (?,?,?,?,?,?,?)""",
                (data["name"], data["cuisine"], data["rating"],
                 data["delivery_time"], data["image"], data["description"],
                 data["active"]),
            )
            flash("Restaurant added.", "success")
        return redirect(url_for("admin.restaurants"))

    return render_template("admin/restaurant_form.html", rest=rest)


@bp.route("/restaurants/<int:rid>/toggle", methods=["POST"])
@admin_required
def restaurant_toggle(rid):
    r = query("SELECT active FROM restaurants WHERE id = ?", (rid,), one=True)
    if r:
        execute("UPDATE restaurants SET active = ? WHERE id = ?",
                (0 if r["active"] else 1, rid))
        flash("Restaurant status updated.", "success")
    return redirect(url_for("admin.restaurants"))


# ---------------------------------------------------------------------------
# Food items
# ---------------------------------------------------------------------------
@bp.route("/food")
@admin_required
def food():
    rows = query(
        """SELECT f.*, r.name AS restaurant_name, c.name AS category_name
           FROM food_items f
           JOIN restaurants r ON r.id = f.restaurant_id
           LEFT JOIN categories c ON c.id = f.category_id
           ORDER BY f.id DESC"""
    )
    return render_template("admin/food.html", foods=rows)


@bp.route("/food/new", methods=["GET", "POST"])
@bp.route("/food/<int:fid>/edit", methods=["GET", "POST"])
@admin_required
def food_form(fid=None):
    item = None
    if fid:
        item = query("SELECT * FROM food_items WHERE id = ?", (fid,), one=True)
        if not item:
            flash("Food item not found.", "error")
            return redirect(url_for("admin.food"))

    if request.method == "POST":
        d = _food_data()
        if not d["name"] or not d["restaurant_id"]:
            flash("Name and restaurant are required.", "error")
        else:
            if fid:
                execute(
                    """UPDATE food_items SET restaurant_id=?, category_id=?,
                       name=?, description=?, price=?, image=?, is_veg=?,
                       popular=?, active=? WHERE id=?""",
                    (d["restaurant_id"], d["category_id"], d["name"],
                     d["description"], d["price"], d["image"], d["is_veg"],
                     d["popular"], d["active"], fid),
                )
                flash("Food item updated.", "success")
            else:
                execute(
                    """INSERT INTO food_items
                       (restaurant_id, category_id, name, description, price,
                        image, is_veg, popular, active)
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (d["restaurant_id"], d["category_id"], d["name"],
                     d["description"], d["price"], d["image"], d["is_veg"],
                     d["popular"], d["active"]),
                )
                flash("Food item added.", "success")
            return redirect(url_for("admin.food"))

    restaurants = query("SELECT id, name FROM restaurants ORDER BY name")
    categories = query("SELECT id, name FROM categories ORDER BY name")
    return render_template("admin/food_form.html", item=item,
                           restaurants=restaurants, categories=categories)


@bp.route("/food/<int:fid>/toggle", methods=["POST"])
@admin_required
def food_toggle(fid):
    f = query("SELECT active FROM food_items WHERE id = ?", (fid,), one=True)
    if f:
        execute("UPDATE food_items SET active = ? WHERE id = ?",
                (0 if f["active"] else 1, fid))
        flash("Food status updated.", "success")
    return redirect(url_for("admin.food"))


# ---------------------------------------------------------------------------
# Categories
# ---------------------------------------------------------------------------
@bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        icon = request.form.get("icon", "").strip() or "🍽️"
        if not name:
            flash("Category name is required.", "error")
        elif query("SELECT id FROM categories WHERE name = ?", (name,), one=True):
            flash("That category already exists.", "error")
        else:
            execute("INSERT INTO categories (name, icon) VALUES (?,?)", (name, icon))
            flash("Category added.", "success")
        return redirect(url_for("admin.categories"))

    rows = query(
        """SELECT c.*,
                  (SELECT COUNT(*) FROM food_items f WHERE f.category_id = c.id)
                      AS food_count
           FROM categories c ORDER BY c.name"""
    )
    return render_template("admin/categories.html", categories=rows)


@bp.route("/categories/<int:cid>/delete", methods=["POST"])
@admin_required
def category_delete(cid):
    execute("DELETE FROM categories WHERE id = ?", (cid,))
    flash("Category deleted.", "success")
    return redirect(url_for("admin.categories"))


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------
@bp.route("/orders")
@admin_required
def orders():
    status = request.args.get("status", "").strip()
    sql = """SELECT o.*, u.name AS customer FROM orders o
             JOIN users u ON u.id = o.user_id"""
    args = []
    if status:
        sql += " WHERE o.status = ?"
        args.append(status)
    sql += " ORDER BY o.id DESC"
    rows = query(sql, args)
    return render_template("admin/orders.html", orders=rows, status=status)


@bp.route("/orders/<int:oid>")
@admin_required
def order_details(oid):
    order = query(
        """SELECT o.*, u.name AS customer, u.email AS customer_email
           FROM orders o JOIN users u ON u.id = o.user_id WHERE o.id = ?""",
        (oid,), one=True,
    )
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("admin.orders"))
    items = query("SELECT * FROM order_items WHERE order_id = ?", (oid,))
    return render_template("admin/order_details.html", order=order, items=items)


@bp.route("/orders/<int:oid>/status", methods=["POST"])
@admin_required
def order_status(oid):
    status = request.form.get("status", "").strip()
    if status not in ORDER_STATUSES:
        flash("Invalid status.", "error")
    else:
        execute("UPDATE orders SET status = ? WHERE id = ?", (status, oid))
        flash(f"Order #{oid} marked {status}.", "success")
    return redirect(request.referrer or url_for("admin.orders"))


# ---------------------------------------------------------------------------
# Form parsing helpers
# ---------------------------------------------------------------------------
def _restaurant_data():
    f = request.form
    return {
        "name": f.get("name", "").strip(),
        "cuisine": f.get("cuisine", "").strip(),
        "rating": f.get("rating", type=float) or 4.0,
        "delivery_time": f.get("delivery_time", "").strip(),
        "image": f.get("image", "").strip(),
        "description": f.get("description", "").strip(),
        "active": 1 if f.get("active") else 0,
    }


def _food_data():
    f = request.form
    return {
        "restaurant_id": f.get("restaurant_id", type=int),
        "category_id": f.get("category_id", type=int),
        "name": f.get("name", "").strip(),
        "description": f.get("description", "").strip(),
        "price": f.get("price", type=float) or 0,
        "image": f.get("image", "").strip(),
        "is_veg": 1 if f.get("is_veg") else 0,
        "popular": 1 if f.get("popular") else 0,
        "active": 1 if f.get("active") else 0,
    }
