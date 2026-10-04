# 🍔 Quickbyte — Food Delivery Web App

A simple, responsive food-delivery web application built with **Python, Flask,
SQLite, HTML, CSS and JavaScript**, implementing the Quickbyte PRD (v1.0).

Customers can browse restaurants, view menus, search food, manage a cart,
checkout (Cash on Delivery) and track orders. Admins can manage restaurants,
food items, categories and orders from a dedicated panel.

---

## ✨ Features

**Customer**
- Register / login / logout (session auth, hashed passwords)
- Home with categories, featured restaurants and popular dishes
- Browse & filter restaurants, view restaurant menus and food details
- Search dishes by name, cuisine or restaurant
- Session cart: add, increase/decrease quantity, remove (live AJAX totals)
- Checkout with delivery details + Cash on Delivery
- Order confirmation, order history and live status timeline

**Admin**
- Separate admin login
- Dashboard with totals (customers, restaurants, food, orders, revenue)
- Manage restaurants (add / edit / show-hide)
- Manage food items (add / edit / show-hide)
- Manage categories (add / delete)
- View orders and update order status

**Security & UX**
- Password hashing (Werkzeug)
- Session-based auth + admin authorization
- CSRF protection on all state-changing requests
- Parameterised SQL (injection-safe)
- User-specific order access
- Responsive design (mobile / tablet / desktop), orange theme `#FF5A1F`
- Real food/restaurant photos with an automatic local placeholder fallback

---

## 🚀 Getting started

```bash
# 1. (optional) create a virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 2. install dependencies
pip install -r requirements.txt

# 3. run the app  (creates & seeds database.db on first run)
python app.py
```

Then open **http://127.0.0.1:5000**

### Demo accounts
| Role     | Email                  | Password  |
|----------|------------------------|-----------|
| Customer | demo@quickbyte.com     | demo123   |
| Admin    | admin@quickbyte.com    | admin123  |

Admin panel: **http://127.0.0.1:5000/admin/login**

---

## 🧪 Tests

An end-to-end smoke test (uses a throwaway DB) exercises the full flow:

```bash
python smoke_test.py
```

---

## 📁 Project structure

```
Food/
├── app.py              # app factory, CSRF, context processors, error handlers
├── db.py               # SQLite connection + schema
├── seed.py             # demo data (users, categories, restaurants, food)
├── helpers.py          # auth decorators, cart logic, CSRF helpers
├── requirements.txt
├── smoke_test.py
├── routes/
│   ├── auth.py         # register / login / logout
│   ├── main.py         # home, restaurants, food, search, cart
│   ├── orders.py       # checkout, place order, history, tracking
│   └── admin.py        # admin login, dashboard, CRUD, orders
├── templates/          # Jinja2 templates (+ templates/admin/)
└── static/
    ├── css/style.css
    └── js/main.js
```

---

## ⚙️ Configuration

- `QUICKBYTE_SECRET` — Flask secret key (set in production).
- `QUICKBYTE_DB` — override the SQLite file path (used by the smoke test).

## 🔮 Future features
Online payments, coupons, reviews & ratings, favourites, notifications,
delivery-partner system and live GPS tracking.
