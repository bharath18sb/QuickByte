"""
Quickbyte - Seed data
Populates the database with an admin, a demo customer, categories,
restaurants (with images) and food items (with images).

Images use Unsplash photo URLs. If a URL ever fails to load, the
front-end (main.js) swaps in a polished local SVG placeholder, so the
UI never shows a broken image.

Seeding is idempotent: it only runs when the tables are empty.
"""
from werkzeug.security import generate_password_hash
from db import get_db, query, execute


def img(photo_id, w=800):
    return (f"https://images.unsplash.com/photo-{photo_id}"
            f"?auto=format&fit=crop&w={w}&q=70")


# ---------------------------------------------------------------------------
# Categories  (name, emoji icon)
# ---------------------------------------------------------------------------
CATEGORIES = [
    ("Pizza",     "🍕", "1513104890138-7c749659a591"),
    ("Burgers",   "🍔", "1568901346375-23c9450c58cd"),
    ("Indian",    "🍛", "1589302168068-964664d93dc0"),
    ("Chinese",   "🥡", "1585032226651-759b368d7246"),
    ("Sushi",     "🍣", "1579584425555-c3ce17fd4351"),
    ("Desserts",  "🍰", "1578985545062-69928b1d9587"),
    ("Beverages", "🥤", "1461023058943-07fcbe16d735"),
    ("Healthy",   "🥗", "1512621776951-a57141f2eefd"),
]

# ---------------------------------------------------------------------------
# Restaurants  (name, cuisine, rating, delivery_time, image_id, description)
# ---------------------------------------------------------------------------
RESTAURANTS = [
    ("Pizza Palace", "Italian, Pizza", 4.6, "25-30 min",
     "1571997478779-2adcbbe9ab2f",
     "Wood-fired artisan pizzas made with fresh dough and premium toppings."),
    ("Burger Barn", "American, Burgers", 4.4, "20-25 min",
     "1550547660-d9450f859349",
     "Juicy hand-pressed burgers, crispy fries and thick shakes."),
    ("Spice Route", "Indian, Biryani", 4.7, "30-40 min",
     "1585937421612-70a008356fbe",
     "Authentic Indian curries, biryanis and tandoor specials."),
    ("Dragon Wok", "Chinese, Asian", 4.3, "25-35 min",
     "1585032226651-759b368d7246",
     "Sizzling wok-tossed noodles, rice bowls and dim sum."),
    ("Sushi Zen", "Japanese, Sushi", 4.8, "35-45 min",
     "1579584425555-c3ce17fd4351",
     "Fresh sushi rolls, ramen and Japanese comfort food."),
    ("Sweet & Sip", "Cafe, Desserts", 4.5, "15-20 min",
     "1578985545062-69928b1d9587",
     "Decadent cakes, ice creams and specialty coffees."),
]

# ---------------------------------------------------------------------------
# Food items
# (restaurant_index, category_name, name, description, price,
#  image_id, is_veg, popular)
# ---------------------------------------------------------------------------
FOODS = [
    # --- Pizza Palace (0) ---
    (0, "Pizza", "Margherita Pizza", "Classic pizza with mozzarella, tomato & fresh basil", 199, "1574071318508-1cdbab80d002", 1, 1),
    (0, "Pizza", "Pepperoni Pizza", "Loaded with spicy pepperoni and extra cheese", 299, "1628840042765-356cda07504e", 0, 1),
    (0, "Pizza", "Veggie Supreme Pizza", "Onion, capsicum, corn, mushroom & olives", 279, "1565299624946-b28f40a0ae38", 1, 0),
    (0, "Pizza", "Garlic Bread Sticks", "Buttery garlic bread with herbs & cheese dip", 129, "1573140247632-f8fd74997d5c", 1, 0),
    (0, "Desserts", "Choco Lava Cake", "Warm chocolate cake with a molten center", 99, "1606313564200-e75d5e30476c", 1, 1),
    (0, "Beverages", "Coca-Cola", "Chilled 500ml soft drink", 60, "1554866585-cd94860890b7", 1, 0),

    # --- Burger Barn (1) ---
    (1, "Burgers", "Classic Cheeseburger", "Beef patty, cheddar, lettuce, tomato & house sauce", 189, "1568901346375-23c9450c58cd", 0, 1),
    (1, "Burgers", "Double Beef Burger", "Two juicy patties with double cheese", 259, "1550547660-d9450f859349", 0, 1),
    (1, "Burgers", "Crispy Chicken Burger", "Fried chicken fillet, mayo & pickles", 199, "1615297928064-24977384d0da", 0, 0),
    (1, "Burgers", "French Fries", "Golden crispy salted fries", 89, "1573080496219-bb080dd4f877", 1, 1),
    (1, "Healthy", "Veg Club Sandwich", "Triple-layer sandwich with fresh veggies", 149, "1528735602780-2552fd46c7af", 1, 0),
    (1, "Beverages", "Chocolate Milkshake", "Thick chocolate shake topped with cream", 129, "1572490122747-3968b75cc699", 1, 0),

    # --- Spice Route (2) ---
    (2, "Indian", "Chicken Biryani", "Fragrant basmati rice layered with spiced chicken", 249, "1642821373181-696a54913e93", 0, 1),
    (2, "Indian", "Butter Chicken", "Tandoori chicken in a creamy tomato gravy", 279, "1585937421612-70a008356fbe", 0, 1),
    (2, "Indian", "Paneer Butter Masala", "Cottage cheese in rich buttery tomato sauce", 229, "1631452180519-c014fe946bc7", 1, 0),
    (2, "Indian", "Butter Naan", "Soft tandoor-baked flatbread with butter", 45, "1601050690597-df0568f70950", 1, 0),
    (2, "Desserts", "Gulab Jamun", "Soft milk dumplings soaked in sugar syrup", 79, "1601050690597-df0568f70950", 1, 0),
    (2, "Beverages", "Mango Lassi", "Sweet yogurt drink blended with mango", 89, "1626200419199-391ae4be7a41", 1, 1),

    # --- Dragon Wok (3) ---
    (3, "Chinese", "Veg Hakka Noodles", "Wok-tossed noodles with crunchy vegetables", 159, "1585032226651-759b368d7246", 1, 1),
    (3, "Chinese", "Chicken Fried Rice", "Egg fried rice with chicken and scallions", 179, "1603133872878-684f208fb84b", 0, 1),
    (3, "Chinese", "Veg Spring Rolls", "Crispy rolls stuffed with vegetables (4 pcs)", 119, "1544025162-d76694265947", 1, 0),
    (3, "Chinese", "Chilli Paneer", "Spicy indo-chinese cottage cheese starter", 189, "1626777552726-4a6b54c97e46", 1, 0),
    (3, "Chinese", "Veg Momos", "Steamed dumplings with spicy chutney (6 pcs)", 109, "1496116218417-1a781b1c416c", 1, 1),

    # --- Sushi Zen (4) ---
    (4, "Sushi", "Salmon Nigiri", "Fresh salmon over seasoned sushi rice (4 pcs)", 329, "1579584425555-c3ce17fd4351", 0, 1),
    (4, "Sushi", "California Roll", "Crab, avocado & cucumber roll (8 pcs)", 289, "1611143669185-af224c5e3252", 0, 1),
    (4, "Sushi", "Spicy Tuna Roll", "Tuna with spicy mayo and sesame (8 pcs)", 309, "1617196034796-73dfa7b1fd56", 0, 0),
    (4, "Sushi", "Chicken Ramen", "Rich broth with noodles, egg and chicken", 259, "1569718212165-3a8278d5f624", 0, 1),
    (4, "Sushi", "Pork Gyoza", "Pan-fried Japanese dumplings (6 pcs)", 199, "1496116218417-1a781b1c416c", 0, 0),

    # --- Sweet & Sip (5) ---
    (5, "Desserts", "Chocolate Fudge Cake", "Rich layered chocolate cake slice", 149, "1578985545062-69928b1d9587", 1, 1),
    (5, "Desserts", "Vanilla Ice Cream", "Two scoops of creamy vanilla", 99, "1497034825429-c343d7c6a68f", 1, 0),
    (5, "Desserts", "Glazed Donut", "Soft donut with sugar glaze", 69, "1551024506-0bccd828d307", 1, 0),
    (5, "Desserts", "Fluffy Pancakes", "Stack of pancakes with maple syrup", 159, "1567620905732-2d1ec7ab7445", 1, 1),
    (5, "Beverages", "Cappuccino", "Espresso topped with steamed milk foam", 119, "1572442388796-11668a67e53d", 1, 0),
    (5, "Beverages", "Cold Coffee", "Chilled blended coffee with ice cream", 139, "1461023058943-07fcbe16d735", 1, 1),
    (5, "Healthy", "Fresh Garden Salad", "Crisp greens, cherry tomato & vinaigrette", 129, "1512621776951-a57141f2eefd", 1, 0),
    (5, "Healthy", "Berry Smoothie", "Mixed berries blended with yogurt", 149, "1505252585461-04db1eb84625", 1, 0),
]


def already_seeded():
    row = query("SELECT COUNT(*) AS c FROM users", one=True)
    return row["c"] > 0


def seed():
    """Insert all seed data. Safe to call multiple times."""
    if already_seeded():
        return False

    # --- users ---
    execute(
        "INSERT INTO users (name, email, password_hash, is_admin) VALUES (?,?,?,?)",
        ("Admin", "admin@quickbyte.com", generate_password_hash("admin123"), 1),
    )
    execute(
        "INSERT INTO users (name, email, password_hash, is_admin) VALUES (?,?,?,?)",
        ("Demo Customer", "demo@quickbyte.com", generate_password_hash("demo123"), 0),
    )

    # --- categories ---
    cat_id = {}
    for name, icon, image_id in CATEGORIES:
        cid = execute(
            "INSERT INTO categories (name, icon, image) VALUES (?,?,?)",
            (name, icon, img(image_id, 400)),
        )
        cat_id[name] = cid

    # --- restaurants ---
    rest_ids = []
    for name, cuisine, rating, delivery, image_id, desc in RESTAURANTS:
        rid = execute(
            """INSERT INTO restaurants
               (name, cuisine, rating, delivery_time, image, description)
               VALUES (?,?,?,?,?,?)""",
            (name, cuisine, rating, delivery, img(image_id), desc),
        )
        rest_ids.append(rid)

    # --- food items ---
    for r_idx, cat, name, desc, price, image_id, is_veg, popular in FOODS:
        execute(
            """INSERT INTO food_items
               (restaurant_id, category_id, name, description, price,
                image, is_veg, popular)
               VALUES (?,?,?,?,?,?,?,?)""",
            (rest_ids[r_idx], cat_id.get(cat), name, desc, price,
             img(image_id), is_veg, popular),
        )

    return True
