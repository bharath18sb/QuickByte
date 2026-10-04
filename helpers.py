"""
Quickbyte - Shared helpers
Auth decorators, current-user lookup, session cart logic and CSRF tokens.
"""
import secrets
from functools import wraps
from flask import session, redirect, url_for, flash, g, request, abort
from db import query

# Flat delivery fee; orders over FREE_ABOVE ship free.
DELIVERY_FEE = 40
FREE_ABOVE = 500

# Order lifecycle (in progression order)
ORDER_STATUSES = [
    "PLACED", "CONFIRMED", "PREPARING",
    "OUT FOR DELIVERY", "DELIVERED", "CANCELLED",
]


# ---------------------------------------------------------------------------
# Current user
# ---------------------------------------------------------------------------
def current_user():
    """Return the logged-in user row (cached on g) or None."""
    if "user" not in g:
        g.user = None
        uid = session.get("user_id")
        if uid:
            g.user = query("SELECT * FROM users WHERE id = ?", (uid,), one=True)
    return g.user


# ---------------------------------------------------------------------------
# Access-control decorators
# ---------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or not user["is_admin"]:
            flash("Admin access required.", "error")
            return redirect(url_for("admin.login"))
        return f(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------------------
# CSRF token
# ---------------------------------------------------------------------------
def get_csrf_token():
    token = session.get("csrf_token")
    if not token:
        token = secrets.token_hex(16)
        session["csrf_token"] = token
    return token


def validate_csrf():
    """Return True if the request carries a valid CSRF token."""
    sent = request.form.get("csrf_token") or request.headers.get("X-CSRFToken")
    real = session.get("csrf_token")
    return bool(real) and bool(sent) and secrets.compare_digest(sent, real)


# ---------------------------------------------------------------------------
# Session cart  ->  { "food_id": quantity }
# ---------------------------------------------------------------------------
def get_cart():
    return session.get("cart", {})


def save_cart(cart):
    session["cart"] = cart
    session.modified = True


def cart_count():
    return sum(get_cart().values())


def cart_add(food_id, qty=1):
    cart = get_cart()
    fid = str(food_id)
    cart[fid] = cart.get(fid, 0) + qty
    if cart[fid] < 1:
        cart.pop(fid, None)
    save_cart(cart)


def cart_set(food_id, qty):
    cart = get_cart()
    fid = str(food_id)
    if qty <= 0:
        cart.pop(fid, None)
    else:
        cart[fid] = qty
    save_cart(cart)


def cart_remove(food_id):
    cart = get_cart()
    cart.pop(str(food_id), None)
    save_cart(cart)


def clear_cart():
    session.pop("cart", None)
    session.modified = True


def cart_details():
    """
    Expand the session cart into full item rows joined with food/restaurant
    data, plus computed totals. Silently drops items that no longer exist.
    Returns dict: items, subtotal, delivery_fee, total, restaurant.
    """
    cart = get_cart()
    items, subtotal = [], 0.0
    valid_cart = {}
    restaurant = None

    for fid, qty in cart.items():
        food = query(
            """SELECT f.*, r.name AS restaurant_name, r.id AS r_id,
                      c.icon AS cat_icon
               FROM food_items f
               JOIN restaurants r ON r.id = f.restaurant_id
               LEFT JOIN categories c ON c.id = f.category_id
               WHERE f.id = ? AND f.active = 1""",
            (fid,), one=True,
        )
        if not food:
            continue
        qty = int(qty)
        line_total = food["price"] * qty
        subtotal += line_total
        valid_cart[fid] = qty
        restaurant = food["restaurant_name"]
        items.append({"food": food, "qty": qty, "line_total": line_total})

    # prune any dead items from the stored cart
    if valid_cart != cart:
        save_cart(valid_cart)

    delivery_fee = 0 if (subtotal == 0 or subtotal >= FREE_ABOVE) else DELIVERY_FEE
    return {
        "items": items,
        "subtotal": subtotal,
        "delivery_fee": delivery_fee,
        "total": subtotal + delivery_fee,
        "restaurant": restaurant,
        "free_above": FREE_ABOVE,
    }
