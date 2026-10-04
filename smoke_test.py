"""End-to-end smoke test for Quickbyte using Flask's test client."""
import os, tempfile
# Use a throwaway database so the real database.db stays clean.
_tmp = os.path.join(tempfile.gettempdir(), "quickbyte_smoke.db")
if os.path.exists(_tmp):
    os.remove(_tmp)
os.environ["QUICKBYTE_DB"] = _tmp

import app as A

c = A.app.test_client()
ok = True

def check(label, cond):
    global ok
    ok = ok and bool(cond)
    print(("PASS" if cond else "FAIL"), "-", label)

def csrf():
    with c.session_transaction() as s:
        return s.get("csrf_token")

# ---- public GET pages ----
for url in ["/", "/restaurants", "/restaurants?category=Pizza",
            "/restaurant/1", "/food/1", "/search?q=biryani",
            "/login", "/register", "/cart", "/admin/login"]:
    r = c.get(url)
    check(f"GET {url}", r.status_code == 200)

# ---- login_required redirect ----
check("checkout redirects when logged out", c.get("/checkout").status_code == 302)

# ---- register (also logs in) ----
c.get("/"); t = csrf()
r = c.post("/register", data=dict(csrf_token=t, name="Test User",
           email="test@example.com", password="secret1", confirm="secret1"),
           follow_redirects=True)
check("register new user", r.status_code == 200 and "Welcome to Quickbyte" in r.text)

# ---- add to cart (AJAX) ----
t = csrf()
r = c.post("/cart/add", data=dict(csrf_token=t, food_id=1, qty=2),
           headers={"X-Requested-With": "XMLHttpRequest"})
j = r.get_json()
check("cart/add returns count 2", r.status_code == 200 and j.get("cart_count") == 2)

t = csrf()
r = c.post("/cart/add", data=dict(csrf_token=t, food_id=5, qty=1),
           headers={"X-Requested-With": "XMLHttpRequest"})
check("cart/add second item", r.get_json().get("cart_count") == 3)

# ---- update cart qty ----
t = csrf()
r = c.post("/cart/update", data=dict(csrf_token=t, food_id=1, qty=1),
           headers={"X-Requested-With": "XMLHttpRequest"})
check("cart/update qty", r.get_json()["cart"]["count"] == 2)

check("cart page renders", c.get("/cart").status_code == 200)

# ---- checkout + place order ----
check("checkout GET", c.get("/checkout").status_code == 200)
t = csrf()
r = c.post("/checkout", data=dict(csrf_token=t, full_name="Test User",
           phone="9876543210", address="12 Main Street", city="Metro City",
           postal_code="560001", payment_method="Cash on Delivery"),
           follow_redirects=True)
check("place order", r.status_code == 200 and "Order placed" in r.text)
check("orders history", c.get("/orders").status_code == 200)
check("order details page", c.get("/order/1").status_code == 200)

# ---- CSRF negative test ----
r = c.post("/cart/add", data=dict(food_id=1),
           headers={"X-Requested-With": "XMLHttpRequest", "X-CSRFToken": "wrong"})
check("CSRF blocks bad token (400)", r.status_code == 400)

# ---- logout ----
t = csrf(); c.post("/logout", data=dict(csrf_token=t))

# ---- admin flow ----
c.get("/admin/login"); t = csrf()
r = c.post("/admin/login", data=dict(csrf_token=t, email="admin@quickbyte.com",
           password="admin123"), follow_redirects=True)
check("admin login", r.status_code == 200 and "Dashboard" in r.text)
for url in ["/admin/", "/admin/restaurants", "/admin/food",
            "/admin/categories", "/admin/orders", "/admin/orders/1"]:
    check(f"admin GET {url}", c.get(url).status_code == 200)

# admin add category
t = csrf()
r = c.post("/admin/categories", data=dict(csrf_token=t, name="Test Snacks",
           icon="🧪"), follow_redirects=True)
check("admin add category", "Test Snacks" in r.text)

# admin add food item
t = csrf()
r = c.post("/admin/food/new", data=dict(csrf_token=t, name="Test Dish",
           restaurant_id=1, category_id=1, price=123, is_veg="on",
           active="on"), follow_redirects=True)
check("admin add food", "Test Dish" in r.text)

# admin update order status
t = csrf()
r = c.post("/admin/orders/1/status", data=dict(csrf_token=t,
           status="CONFIRMED"), follow_redirects=True)
check("admin update order status", "CONFIRMED" in r.text)

# ---- 404 handler ----
check("404 page", c.get("/no-such-page").status_code == 404)

print("\nRESULT:", "ALL PASS" if ok else "SOME FAILED")
import sys
sys.exit(0 if ok else 1)
