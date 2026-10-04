# 🍔 QuickByte — Food Delivery Web App

QuickByte is a full-stack food delivery web application built with **Python, Flask, SQLite, HTML, CSS, and JavaScript**.

The application allows customers to discover restaurants, browse menus, search for food, manage their cart, place Cash on Delivery orders, and track their orders. It also includes a dedicated admin panel for managing restaurants, food items, categories, and orders.

---

## ✨ Features

### 👤 Customer

- Register, login, and logout
- Session-based authentication
- Password hashing
- Browse food categories
- Browse and filter restaurants
- View restaurant menus and food details
- Search dishes by name, cuisine, or restaurant
- Session-based shopping cart
- Add, increase, decrease, and remove cart items
- Live cart totals using AJAX
- Checkout with delivery details
- Cash on Delivery
- Order confirmation
- Order history
- Order status timeline

### 🔐 Admin

- Separate admin authentication
- Admin dashboard with:
  - Customers
  - Restaurants
  - Food items
  - Orders
  - Revenue
- Add and edit restaurants
- Show/hide restaurants
- Add and edit food items
- Show/hide food items
- Add and delete categories
- View customer orders
- Update order status

### 🛡️ Security & UX

- Password hashing using Werkzeug
- Session-based authentication
- Admin authorization
- CSRF protection for state-changing requests
- Parameterized SQL queries
- User-specific order access
- Responsive design for mobile, tablet, and desktop
- Orange-themed UI (`#FF5A1F`)
- Real food and restaurant images
- Automatic local placeholder fallback

---

## 🛠️ Tech Stack

### Frontend

- HTML5
- CSS3
- JavaScript
- Jinja2 Templates
- AJAX

### Backend

- Python
- Flask
- Werkzeug

### Database

- SQLite

### Testing

- Python-based end-to-end smoke test

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/QuickByte.git
cd QuickByte
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate the virtual environment

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the application

```bash
python app.py
```

The application will create and seed the SQLite database on first run.

Open:

```text
http://127.0.0.1:5000
```

---

## 🔑 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Customer | `demo@quickbyte.com` | `demo123` |
| Admin | `admin@quickbyte.com` | `admin123` |

### Admin Panel

```text
http://127.0.0.1:5000/admin/login
```

> These credentials are intended only for local/demo use.

---

## 🧪 Testing

QuickByte includes an end-to-end smoke test that uses a throwaway database and exercises the main application flow.

Run:

```bash
python smoke_test.py
```

---

## 📸 Screenshots

Screenshots of the application will be added here.
## 📸 Screenshots

### 🏠 Home Page

![QuickByte Home](screenshots/home.png)

### 🍽️ Restaurant & Menu

![Restaurant Menu](screenshots/restaurant.png)

### 🛒 Shopping Cart

![Shopping Cart](screenshots/cart.png)

### 💳 Checkout

![Checkout](screenshots/checkout.png)

### 📦 Orders & Tracking

![Orders](screenshots/orders.png)

### 🔐 Admin Dashboard

![Admin Dashboard](screenshots/admin-dashboard.png)


---

## 📁 Project Structure

```text
Food/
├── app.py                  # Flask application entry point
├── db.py                   # SQLite connection and database schema
├── seed.py                 # Demo data and database seeding
├── helpers.py              # Authentication, cart and CSRF helpers
├── requirements.txt        # Python dependencies
├── smoke_test.py           # End-to-end smoke test
│
├── routes/
│   ├── __init__.py
│   ├── auth.py             # Registration, login and logout
│   ├── main.py             # Home, restaurants, food, search and cart
│   ├── orders.py           # Checkout, orders and tracking
│   └── admin.py            # Admin dashboard and management
│
├── templates/
│   ├── admin/              # Admin dashboard templates
│   └── ...                 # Customer-facing templates
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

---

## ⚙️ Configuration

QuickByte supports the following environment variables:

| Variable | Description |
|----------|-------------|
| `QUICKBYTE_SECRET` | Flask secret key. Set this in production. |
| `QUICKBYTE_DB` | Optional SQLite database path. Used by the smoke test. |

For production, use environment variables instead of hardcoding sensitive configuration.

---

## 🔒 Security

QuickByte implements several security practices:

- Password hashing with Werkzeug
- Session-based authentication
- Admin authorization
- CSRF protection
- Parameterized SQL queries
- User-specific order authorization
- Environment-based secret configuration

---

## 🔮 Future Improvements

Planned features include:

- 💳 Online payments
- 🎟️ Coupons and discount codes
- ⭐ Reviews and ratings
- ❤️ Favourite restaurants and dishes
- 🔔 Order notifications
- 📍 Delivery tracking
- 📱 Improved mobile experience

---

## 👨‍💻 Author

**Bharath S B**

Built as a full-stack web development project using Flask and SQLite.

---

## ⭐ Project

If you find the project interesting, consider giving the repository a ⭐ on GitHub.
