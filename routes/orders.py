"""Order routes: checkout, place order, confirmation, history, details."""
from flask import (
    Blueprint, render_template, request, redirect, url_for, flash,
)

from db import query, execute
from helpers import login_required, current_user, cart_details, clear_cart

bp = Blueprint("orders", __name__)


@bp.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    cart = cart_details()
    if not cart["items"]:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("main.cart"))

    user = current_user()
    # pre-fill from the user's most recent saved address
    last = query(
        "SELECT * FROM addresses WHERE user_id = ? ORDER BY id DESC LIMIT 1",
        (user["id"],), one=True,
    )

    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        city = request.form.get("city", "").strip()
        postal_code = request.form.get("postal_code", "").strip()
        payment_method = request.form.get("payment_method", "Cash on Delivery")

        errors = []
        if len(full_name) < 2:
            errors.append("Please enter your name.")
        if not phone.isdigit() or not (7 <= len(phone) <= 15):
            errors.append("Please enter a valid phone number.")
        if len(address) < 5:
            errors.append("Please enter your delivery address.")
        if not city:
            errors.append("Please enter your city.")
        if not postal_code:
            errors.append("Please enter your postal code.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("checkout.html", cart=cart,
                                   form=request.form)

        # Re-read cart totals server-side (never trust the client).
        cart = cart_details()
        if not cart["items"]:
            flash("Your cart is empty.", "warning")
            return redirect(url_for("main.cart"))

        order_id = execute(
            """INSERT INTO orders
               (user_id, full_name, phone, address, city, postal_code,
                payment_method, subtotal, delivery_fee, total, status)
               VALUES (?,?,?,?,?,?,?,?,?,?,'PLACED')""",
            (user["id"], full_name, phone, address, city, postal_code,
             payment_method, cart["subtotal"], cart["delivery_fee"],
             cart["total"]),
        )
        for it in cart["items"]:
            f = it["food"]
            execute(
                """INSERT INTO order_items
                   (order_id, food_id, food_name, price, quantity)
                   VALUES (?,?,?,?,?)""",
                (order_id, f["id"], f["name"], f["price"], it["qty"]),
            )

        # save the address for next time
        execute(
            """INSERT INTO addresses
               (user_id, full_name, phone, address, city, postal_code)
               VALUES (?,?,?,?,?,?)""",
            (user["id"], full_name, phone, address, city, postal_code),
        )

        clear_cart()
        flash("Order placed successfully!", "success")
        return redirect(url_for("orders.confirmation", oid=order_id))

    return render_template("checkout.html", cart=cart, form=last or {})


@bp.route("/order-confirmation/<int:oid>")
@login_required
def confirmation(oid):
    order, items = _get_order(oid)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders.my_orders"))
    return render_template("order_confirmation.html", order=order, items=items)


@bp.route("/orders")
@login_required
def my_orders():
    user = current_user()
    rows = query(
        """SELECT o.*,
                  (SELECT COUNT(*) FROM order_items oi WHERE oi.order_id = o.id)
                      AS item_count
           FROM orders o WHERE o.user_id = ?
           ORDER BY o.id DESC""",
        (user["id"],),
    )
    return render_template("orders.html", orders=rows)


@bp.route("/order/<int:oid>")
@login_required
def order_details(oid):
    order, items = _get_order(oid)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for("orders.my_orders"))
    return render_template("order_details.html", order=order, items=items)


def _get_order(oid):
    """Fetch an order + items, enforcing that it belongs to the current user."""
    user = current_user()
    order = query(
        "SELECT * FROM orders WHERE id = ? AND user_id = ?",
        (oid, user["id"]), one=True,
    )
    if not order:
        return None, []
    items = query("SELECT * FROM order_items WHERE order_id = ?", (oid,))
    return order, items
