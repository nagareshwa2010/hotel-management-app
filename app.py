import os
from flask import Flask, request, render_template_string, redirect, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nr_hotel_secret_key_v3")

# Database Initialization with Auto-Migration Fix
def init_db():
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    
    # 1. Bookings Table Creation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            room_type TEXT NOT NULL,
            nights INTEGER NOT NULL,
            meal_plan TEXT DEFAULT 'No Meal (Room Only)',
            total_price INTEGER NOT NULL
        )
    ''')
    
    # 2. Migration Check: Ensure meal_plan column exists in existing database
    cursor.execute("PRAGMA table_info(bookings)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'meal_plan' not in columns:
        cursor.execute("ALTER TABLE bookings ADD COLUMN meal_plan TEXT DEFAULT 'No Meal (Room Only)'")
        
    conn.commit()
    conn.close()

# Run DB initialization safely
try:
    init_db()
except Exception as e:
    print(f"Database setup note: {e}")

# Rooms Data
ROOMS_DATA = [
    {"id": 1, "name": "Standard Room", "price": 2000, "desc": "Cozy queen bed, AC, Free Wi-Fi, and Work desk.", "img": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=500&q=80"},
    {"id": 2, "name": "Deluxe Suite", "price": 5000, "desc": "King size bed, Ocean view, Free Wi-Fi, and Breakfast.", "img": "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=500&q=80"},
    {"id": 3, "name": "Executive Suite", "price": 8000, "desc": "Private balcony, Jacuzzi, Mini-bar, Room Service.", "img": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=500&q=80"},
    {"id": 4, "name": "Family Suite", "price": 10000, "desc": "Spacious room with 2 King beds, living space, and kids area access.", "img": "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?auto=format&fit=crop&w=500&q=80"},
    {"id": 5, "name": "Presidential Suite", "price": 15000, "desc": "Penthouse view, Private pool, Personal Butler service.", "img": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=500&q=80"},
    {"id": 6, "name": "Penthouse Suite", "price": 20000, "desc": "Top floor panoramic city view, private terrace, and plunge pool.", "img": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=500&q=80"}
]

# Base Layout
BASE_HTML = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NR Hotel Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Poppins', sans-serif; background-color: #f4f6f9; overflow-x: hidden; }
        h1, h2, h3, .brand-title { font-family: 'Playfair Display', serif; }
        .sidebar { min-height: 100vh; background-color: #0b132b; color: #ffffff; }
        .sidebar .nav-link { color: #a0aec0; padding: 12px 20px; font-size: 1.05rem; border-radius: 8px; margin-bottom: 5px; }
        .sidebar .nav-link:hover, .sidebar .nav-link.active { color: #d4af37; background-color: #1c2541; }
        .sidebar .nav-link i { margin-right: 10px; }
        .brand-title { color: #d4af37; font-size: 1.8rem; font-weight: 700; }
        .price-tag { color: #d4af37; font-weight: 600; font-size: 1.2rem; }
        .btn-gold { background-color: #d4af37; color: #0b132b; font-weight: 600; border: none; }
        .btn-gold:hover { background-color: #b59226; color: white; }
        .hero-banner {
            background: linear-gradient(rgba(11, 19, 43, 0.75), rgba(11, 19, 43, 0.75)), 
                        url('https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1350&q=80');
            background-size: cover; background-position: center;
            color: white; border-radius: 15px; padding: 60px 30px; text-align: center;
        }
        .badge-available { background-color: #28a745; }
        .badge-booked { background-color: #dc3545; }
    </style>
</head>
<body>

<div class="container-fluid">
    <div class="row">
        <!-- Left Sidebar -->
        <div class="col-md-3 col-lg-2 sidebar p-3 d-flex flex-column">
            <div class="brand-title my-3 text-center">🏰 NR Hotel</div>
            <hr class="text-secondary">
            <ul class="nav nav-pills flex-column mb-auto">
                <li class="nav-item">
                    <a href="/" class="nav-link {% if active_page == 'home' %}active{% endif %}">
                        <i class="bi bi-house-door-fill"></i> Home
                    </a>
                </li>
                <li>
                    <a href="/rooms" class="nav-link {% if active_page == 'rooms' %}active{% endif %}">
                        <i class="bi bi-door-open-fill"></i> Explore Rooms
                    </a>
                </li>
                <li>
                    <a href="/book_page" class="nav-link {% if active_page == 'book' %}active{% endif %}">
                        <i class="bi bi-calendar-check-fill"></i> Book Room
                    </a>
                </li>
                <li>
                    <a href="/status" class="nav-link {% if active_page == 'status' %}active{% endif %}">
                        <i class="bi bi-card-checklist"></i> Bookings & Status
                    </a>
                </li>
            </ul>
            <hr class="text-secondary">
            <div class="text-center text-muted small">© 2026 NR Hotel Group</div>
        </div>

        <!-- Main Content Area -->
        <div class="col-md-9 col-lg-10 p-4">
            {% block content %}{% endblock %}
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Templates
HOME_TEMPLATE = BASE_HTML + """
{% block content %}
<div class="hero-banner mb-4">
    <h1 class="display-4 fw-bold">Welcome to NR Hotel</h1>
    <p class="lead">Experience World-Class Luxury, Elegant Rooms & Dining</p>
    <a href="/rooms" class="btn btn-gold btn-lg mt-3">Explore All Rooms</a>
</div>
<div class="row text-center g-4 my-3">
    <div class="col-md-4">
        <div class="p-4 bg-white rounded-3 shadow-sm">
            <i class="bi bi-cup-hot-fill fs-1 text-warning"></i>
            <h4 class="mt-3">Meal Plans</h4>
            <p class="text-muted">Choose from Breakfast Only, Half Board, or Premium Full Board options.</p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="p-4 bg-white rounded-3 shadow-sm">
            <i class="bi bi-shield-check fs-1 text-success"></i>
            <h4 class="mt-3">Instant Booking</h4>
            <p class="text-muted">Easily reserve suites online with flexible options and dynamic pricing.</p>
        </div>
    </div>
    <div class="col-md-4">
        <div class="p-4 bg-white rounded-3 shadow-sm">
            <i class="bi bi-building-check fs-1 text-primary"></i>
            <h4 class="mt-3">Real-time Status</h4>
            <p class="text-muted">Check live room availability and view current reservation lists anytime.</p>
        </div>
    </div>
</div>
{% endblock %}
"""

ROOMS_TEMPLATE = BASE_HTML + """
{% block content %}
<h2 class="mb-4">Our Rooms & Suites</h2>
<div class="row g-4">
    {% for room in rooms %}
    <div class="col-md-4">
        <div class="card h-100 border-0 shadow-sm rounded-3">
            <img src="{{ room.img }}" class="card-img-top" style="height: 200px; object-fit: cover;">
            <div class="card-body">
                <h4>{{ room.name }}</h4>
                <p class="text-muted small">{{ room.desc }}</p>
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <span class="price-tag">₹{{ room.price }} / night</span>
                    <a href="/book_page?room={{ room.name }}" class="btn btn-gold btn-sm">Book Now</a>
                </div>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endblock %}
"""

BOOKING_TEMPLATE = BASE_HTML + """
{% block content %}
<div class="container" style="max-width: 650px;">
    <div class="bg-white p-4 rounded-3 shadow-sm">
        <h3 class="mb-4 text-center">Room Reservation</h3>
        <form action="/book" method="POST">
            <div class="mb-3">
                <label class="form-label fw-bold">Guest Name</label>
                <input type="text" name="guest_name" class="form-control" placeholder="Enter guest name" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-bold">Select Room Type</label>
                <select name="room_type" class="form-select">
                    {% for room in rooms %}
                    <option value="{{ room.name }}" {% if selected_room == room.name %}selected{% endif %}>
                        {{ room.name }} - ₹{{ room.price }}/night
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label fw-bold">Select Meal Plan</label>
                <select name="meal_plan" class="form-select">
                    <option value="No Meal (Room Only)">No Meal (Room Only) - ₹0</option>
                    <option value="Breakfast Included">Breakfast Included - ₹500/night</option>
                    <option value="Half Board (Breakfast + Dinner)">Half Board (Breakfast + Dinner) - ₹1,200/night</option>
                    <option value="Full Board (All Meals Included)">Full Board (All Meals Included) - ₹2,000/night</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label fw-bold">Number of Nights</label>
                <input type="number" name="nights" class="form-control" min="1" value="1" required>
            </div>
            <button type="submit" class="btn btn-gold w-100 py-2">Confirm Booking</button>
        </form>
    </div>
</div>
{% endblock %}
"""

STATUS_TEMPLATE = BASE_HTML + """
{% block content %}
<h2 class="mb-4">Room Availability & Live Bookings</h2>
<div class="card border-0 shadow-sm mb-5">
    <div class="card-header bg-dark text-white fw-bold">Room Availability Overview</div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr>
                        <th>Room Type</th>
                        <th>Standard Rate</th>
                        <th>Status</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in availability %}
                    <tr>
                        <td class="fw-bold">{{ item.name }}</td>
                        <td>₹{{ item.price }} / night</td>
                        <td>
                            {% if item.is_booked %}
                            <span class="badge badge-booked">Booked (Not Available)</span>
                            {% else %}
                            <span class="badge badge-available">Available</span>
                            {% endif %}
                        </td>
                        <td>
                            {% if not item.is_booked %}
                            <a href="/book_page?room={{ item.name }}" class="btn btn-gold btn-sm">Book This</a>
                            {% else %}
                            <button class="btn btn-secondary btn-sm" disabled>Occupied</button>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

<div class="card border-0 shadow-sm">
    <div class="card-header bg-dark text-white fw-bold">Recent Reservations List</div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-striped mb-0">
                <thead class="table-light">
                    <tr>
                        <th>#</th>
                        <th>Guest Name</th>
                        <th>Room Type</th>
                        <th>Meal Plan</th>
                        <th>Nights</th>
                        <th>Total Price</th>
                    </tr>
                </thead>
                <tbody>
                    {% for b in bookings %}
                    <tr>
                        <td>{{ b[0] }}</td>
                        <td class="fw-bold">{{ b[1] }}</td>
                        <td>{{ b[2] }}</td>
                        <td><span class="badge bg-info text-dark">{{ b[4] if b|length > 4 else 'N/A' }}</span></td>
                        <td>{{ b[3] }}</td>
                        <td class="text-success fw-bold">₹{{ b[5] if b|length > 5 else b[4] }}</td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="6" class="text-center text-muted p-3">No bookings recorded yet.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
"""

# Routes
@app.route('/')
def home():
    init_db()
    return render_template_string(HOME_TEMPLATE, active_page='home')

@app.route('/rooms')
def rooms():
    return render_template_string(ROOMS_TEMPLATE, rooms=ROOMS_DATA, active_page='rooms')

@app.route('/book_page')
def book_page():
    selected_room = request.args.get('room', '')
    return render_template_string(BOOKING_TEMPLATE, rooms=ROOMS_DATA, selected_room=selected_room, active_page='book')

@app.route('/book', methods=['POST'])
def book():
    init_db()
    guest_name = request.form.get('guest_name')
    room_type = request.form.get('room_type')
    meal_plan = request.form.get('meal_plan')
    nights = int(request.form.get('nights', 1))
    
    room_price = next((r['price'] for r in ROOMS_DATA if r['name'] == room_type), 2000)
    meal_prices = {
        "No Meal (Room Only)": 0,
        "Breakfast Included": 500,
        "Half Board (Breakfast + Dinner)": 1200,
        "Full Board (All Meals Included)": 2000
    }
    meal_price = meal_prices.get(meal_plan, 0)
    total_price = (room_price + meal_price) * nights
    
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bookings (guest_name, room_type, nights, meal_plan, total_price) VALUES (?, ?, ?, ?, ?)",
                   (guest_name, room_type, nights, meal_plan, total_price))
    conn.commit()
    conn.close()
    
    return redirect(url_for('status'))

@app.route('/status')
def status():
    init_db()
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
    bookings = cursor.fetchall()
    conn.close()
    
    booked_room_names = [b[2] for b in bookings]
    availability = []
    for r in ROOMS_DATA:
        availability.append({
            "name": r["name"],
            "price": r["price"],
            "is_booked": r["name"] in booked_room_names
        })
        
    return render_template_string(STATUS_TEMPLATE, bookings=bookings, availability=availability, active_page='status')

if __name__ == '__main__':
    app.run(debug=True)
