"""Main customer routes: home, restaurants, food, search, cart."""
from collections import OrderedDict
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, jsonify,
)

from db import query
from helpers import (
    cart_add, cart_set, cart_remove, cart_details, cart_count,
)

bp = Blueprint("main", __name__)


def _wants_json():
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"


@bp.route("/")
def index():
    categories = query("SELECT * FROM categories ORDER BY name")
    featured = query(
        "SELECT * FROM restaurants WHERE active = 1 ORDER BY rating DESC LIMIT 6"
    )
    popular = query(
        """SELECT f.*, r.name AS restaurant_name, c.icon AS cat_icon
           FROM food_items f
           JOIN restaurants r ON r.id = f.restaurant_id
           LEFT JOIN categories c ON c.id = f.category_id
           WHERE f.active = 1 AND f.popular = 1
           ORDER BY RANDOM() LIMIT 8"""
    )
    return render_template("index.html", categories=categories,
                           featured=featured, popular=popular)


@bp.route("/restaurants")
def restaurants():
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "").strip()

    sql = "SELECT * FROM restaurants WHERE active = 1"
    args = []
    if q:
        sql += " AND (name LIKE ? OR cuisine LIKE ?)"
        args += [f"%{q}%", f"%{q}%"]
    if category:
        sql += """ AND id IN (
                    SELECT f.restaurant_id FROM food_items f
                    JOIN categories c ON c.id = f.category_id
                    WHERE c.name = ? AND f.active = 1)"""
        args.append(category)
    sql += " ORDER BY rating DESC"

    rows = query(sql, args)
    return render_template("restaurants.html", restaurants=rows,
                           q=q, category=category)


@bp.route("/restaurant/<int:rid>")
def restaurant(rid):
    rest = query(
        "SELECT * FROM restaurants WHERE id = ? AND active = 1", (rid,), one=True
    )
    if not rest:
        flash("Restaurant not found.", "error")
        return redirect(url_for("main.restaurants"))

    foods = query(
        """SELECT f.*, c.name AS category_name, c.icon AS cat_icon
           FROM food_items f
           LEFT JOIN categories c ON c.id = f.category_id
           WHERE f.restaurant_id = ? AND f.active = 1
           ORDER BY c.name, f.name""",
        (rid,),
    )

    # group items by category for a menu-style layout
    menu = OrderedDict()
    for f in foods:
        key = f["category_name"] or "Others"
        menu.setdefault(key, []).append(f)

    return render_template("restaurant.html", restaurant=rest, menu=menu)


@bp.route("/food/<int:fid>")
def food(fid):
    item = query(
        """SELECT f.*, r.name AS restaurant_name, r.id AS r_id,
                  r.delivery_time, r.rating AS r_rating,
                  c.name AS category_name, c.icon AS cat_icon
           FROM food_items f
           JOIN restaurants r ON r.id = f.restaurant_id
           LEFT JOIN categories c ON c.id = f.category_id
           WHERE f.id = ? AND f.active = 1""",
        (fid,), one=True,
    )
    if not item:
        flash("Food item not found.", "error")
        return redirect(url_for("main.index"))

    related = query(
        """SELECT f.*, c.icon AS cat_icon FROM food_items f
           LEFT JOIN categories c ON c.id = f.category_id
           WHERE f.restaurant_id = ? AND f.id != ? AND f.active = 1
           ORDER BY RANDOM() LIMIT 4""",
        (item["r_id"], fid),
    )
    return render_template("food.html", item=item, related=related)


@bp.route("/search")
def search():
    q = request.args.get("q", "").strip()
    results = []
    if q:
        results = query(
            """SELECT f.*, r.name AS restaurant_name, r.id AS r_id,
                      c.icon AS cat_icon
               FROM food_items f
               JOIN restaurants r ON r.id = f.restaurant_id
               LEFT JOIN categories c ON c.id = f.category_id
               WHERE f.active = 1 AND (f.name LIKE ? OR f.description LIKE ?
                     OR c.name LIKE ? OR r.name LIKE ?)
               ORDER BY f.popular DESC, f.name""",
            (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"),
        )
    return render_template("search.html", q=q, results=results)


# ---------------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------------
@bp.route("/cart")
def cart():
    return render_template("cart.html", cart=cart_details())


@bp.route("/cart/add", methods=["POST"])
def cart_add_route():
    fid = request.form.get("food_id", type=int)
    qty = request.form.get("qty", default=1, type=int) or 1
    item = query(
        "SELECT * FROM food_items WHERE id = ? AND active = 1", (fid,), one=True
    )
    if not item:
        if _wants_json():
            return jsonify(ok=False, error="Item unavailable"), 404
        flash("That item is not available.", "error")
        return redirect(request.referrer or url_for("main.index"))

    cart_add(fid, max(1, qty))
    if _wants_json():
        return jsonify(ok=True, cart_count=cart_count(),
                       message=f"{item['name']} added to cart")
    flash(f"{item['name']} added to cart.", "success")
    return redirect(request.referrer or url_for("main.cart"))


@bp.route("/cart/update", methods=["POST"])
def cart_update_route():
    fid = request.form.get("food_id", type=int)
    qty = request.form.get("qty", type=int)
    if fid is not None and qty is not None:
        cart_set(fid, qty)
    if _wants_json():
        c = cart_details()
        return jsonify(ok=True, cart=_cart_json(c))
    return redirect(url_for("main.cart"))


@bp.route("/cart/remove", methods=["POST"])
def cart_remove_route():
    fid = request.form.get("food_id", type=int)
    if fid is not None:
        cart_remove(fid)
    if _wants_json():
        c = cart_details()
        return jsonify(ok=True, cart=_cart_json(c))
    flash("Item removed from cart.", "success")
    return redirect(url_for("main.cart"))


def _cart_json(c):
    """Serialise cart totals for AJAX updates."""
    return {
        "count": cart_count(),
        "subtotal": round(c["subtotal"], 2),
        "delivery_fee": c["delivery_fee"],
        "total": round(c["total"], 2),
        "lines": {str(i["food"]["id"]): round(i["line_total"], 2)
                  for i in c["items"]},
        "empty": len(c["items"]) == 0,
    }
