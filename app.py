import os
import sqlite3
from datetime import datetime
from flask import Flask, request, render_template_string, redirect, url_for, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nr_hotel_secret_key_v4")

# Database Initialization
def init_db():
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    
    # 1. Users Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Migration check for is_admin column
    cursor.execute("PRAGMA table_info(users)")
    user_columns = [column[1] for column in cursor.fetchall()]
    if 'is_admin' not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0")

    # Default Admin user (admin / admin123)
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ("admin", "admin123", 1))

    # Default Guest user account
    cursor.execute("SELECT * FROM users WHERE username = 'Guest_User'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", ("Guest_User", "guestpass", 0))

    # 2. Active User Sessions Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS active_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            login_time TEXT NOT NULL
        )
    ''')

    # 3. Bookings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            room_type TEXT NOT NULL,
            nights INTEGER NOT NULL,
            meal_plan TEXT DEFAULT 'No Meal (Room Only)',
            total_price INTEGER NOT NULL,
            status TEXT DEFAULT 'Booked'
        )
    ''')
    
    cursor.execute("PRAGMA table_info(bookings)")
    booking_columns = [column[1] for column in cursor.fetchall()]
    if 'status' not in booking_columns:
        cursor.execute("ALTER TABLE bookings ADD COLUMN status TEXT DEFAULT 'Booked'")
        
    conn.commit()
    conn.close()

try:
    init_db()
except Exception as e:
    print(f"Database setup note: {e}")

# Helper Functions
def is_admin_user():
    if 'username' not in session:
        return False
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("SELECT is_admin FROM users WHERE username = ?", (session['username'],))
    user = cursor.fetchone()
    conn.close()
    return user and user[0] == 1

def log_user_session(username):
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT OR REPLACE INTO active_sessions (username, login_time) VALUES (?, ?)", (username, login_time))
    conn.commit()
    conn.close()

def clear_user_session(username):
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM active_sessions WHERE username = ?", (username,))
    conn.commit()
    conn.close()

# Rooms Data
ROOMS_DATA = [
    {"id": 1, "name": "Standard Room", "price": 2000, "desc": "Cozy queen bed, AC, Free Wi-Fi, and Work desk.", "img": "https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=500&q=80"},
    {"id": 2, "name": "Deluxe Suite", "price": 5000, "desc": "King size bed, Ocean view, Free Wi-Fi, and Breakfast.", "img": "https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=500&q=80"},
    {"id": 3, "name": "Executive Suite", "price": 8000, "desc": "Private balcony, Jacuzzi, Mini-bar, Room Service.", "img": "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=500&q=80"},
    {"id": 4, "name": "Family Suite", "price": 10000, "desc": "Spacious room with 2 King beds, living space, and kids area access.", "img": "https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?auto=format&fit=crop&w=500&q=80"},
    {"id": 5, "name": "Presidential Suite", "price": 15000, "desc": "Penthouse view, Private pool, Personal Butler service.", "img": "https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=500&q=80"},
    {"id": 6, "name": "Penthouse Suite", "price": 20000, "desc": "Top floor panoramic city view, private terrace, and plunge pool.", "img": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=500&q=80"}
]

# Base Layout Template
BASE_LAYOUT = """
<!DOCTYPE html>
<html lang="en">
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
            
            {% if session.get('username') %}
            <div class="text-center text-warning mb-2 small">
                <i class="bi bi-person-circle"></i> Logged in as: <strong>{{ session.get('username') }}</strong>
                {% if is_admin %}<br><span class="badge bg-danger mt-1">Admin</span>{% endif %}
            </div>
            {% endif %}

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
                <hr class="text-secondary">
                {% if session.get('username') %}
                <li>
                    <a href="/logout" class="nav-link text-danger">
                        <i class="bi bi-box-arrow-right"></i> Logout
                    </a>
                </li>
                {% else %}
                <li>
                    <a href="/login" class="nav-link {% if active_page == 'login' %}active{% endif %}">
                        <i class="bi bi-box-arrow-in-right"></i> Login
                    </a>
                </li>
                <li>
                    <a href="/register" class="nav-link {% if active_page == 'register' %}active{% endif %}">
                        <i class="bi bi-person-plus-fill"></i> Register
                    </a>
                </li>
                <li>
                    <a href="/guest_login" class="nav-link text-info">
                        <i class="bi bi-person-badge-fill"></i> Guest Login
                    </a>
                </li>
                {% endif %}
            </ul>
            <hr class="text-secondary">
            <div class="text-center text-muted small">© 2026 NR Hotel Group</div>
        </div>

        <!-- Main Content Area -->
        <div class="col-md-9 col-lg-10 p-4">
            BODY_CONTENT
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

# Page Templates
HOME_CONTENT = """
<div class="hero-banner mb-4">
    <h1 class="display-4 fw-bold">Welcome to NR Hotel</h1>
    <p class="lead">Experience World-Class Luxury, Elegant Rooms & Dining</p>
    <a href="/rooms" class="btn btn-gold btn-lg mt-3">Explore All Rooms</a>
</div>
"""

LOGIN_CONTENT = """
<div class="container" style="max-width: 450px;">
    <div class="bg-white p-4 rounded-3 shadow-sm mt-5">
        <h3 class="mb-4 text-center">Login</h3>
        {% if error %}<div class="alert alert-danger">{{ error }}</div>{% endif %}
        <form action="/login" method="POST">
            <div class="mb-3">
                <label class="form-label fw-bold">Username</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-bold">Password</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-gold w-100 py-2">Login</button>
        </form>
        <hr>
        <div class="text-center">
            <a href="/guest_login" class="btn btn-outline-info w-100 py-2 mb-2">
                <i class="bi bi-person-badge-fill"></i> Continue as Guest
            </a>
            <small class="text-muted">Default Admin Credentials: <b>admin / admin123</b></small>
        </div>
    </div>
</div>
"""

REGISTER_CONTENT = """
<div class="container" style="max-width: 450px;">
    <div class="bg-white p-4 rounded-3 shadow-sm mt-5">
        <h3 class="mb-4 text-center">Register Account</h3>
        {% if error %}<div class="alert alert-danger">{{ error }}</div>{% endif %}
        <form action="/register" method="POST">
            <div class="mb-3">
                <label class="form-label fw-bold">Choose Username</label>
                <input type="text" name="username" class="form-control" required>
            </div>
            <div class="mb-3">
                <label class="form-label fw-bold">Choose Password</label>
                <input type="password" name="password" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-gold w-100 py-2">Register</button>
        </form>
        <hr>
        <div class="text-center">
            <a href="/guest_login" class="btn btn-outline-info w-100 py-2">
                <i class="bi bi-person-badge-fill"></i> Continue as Guest
            </a>
        </div>
    </div>
</div>
"""

ROOMS_CONTENT = """
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
"""

BOOKING_CONTENT = """
<div class="container" style="max-width: 650px;">
    <div class="bg-white p-4 rounded-3 shadow-sm">
        <h3 class="mb-4 text-center">Room Reservation</h3>
        <form action="/book" method="POST">
            <div class="mb-3">
                <label class="form-label fw-bold">Guest Name</label>
                <input type="text" name="guest_name" class="form-control" value="{{ session.get('username', '') }}" required>
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
"""

STATUS_CONTENT = """
<h2 class="mb-4">Room Availability & Dashboard</h2>

{% if is_admin %}
<!-- Admin Dashboard: Currently Logged-In Users -->
<div class="card border-0 shadow-sm mb-5">
    <div class="card-header bg-danger text-white fw-bold d-flex justify-content-between align-items-center">
        <span><i class="bi bi-people-fill"></i> Admin Panel: Currently Logged-In Users</span>
        <span class="badge bg-light text-dark">{{ active_users|length }} Active Session(s)</span>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover mb-0">
                <thead class="table-light">
                    <tr>
                        <th>#</th>
                        <th>Username</th>
                        <th>Login Timestamp</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user in active_users %}
                    <tr>
                        <td>{{ loop.index }}</td>
                        <td class="fw-bold text-primary">
                            <i class="bi bi-person-circle"></i> {{ user[1] }}
                        </td>
                        <td>{{ user[2] }}</td>
                        <td><span class="badge bg-success"><i class="bi bi-dot"></i> Online</span></td>
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="4" class="text-center text-muted p-3">No active users recorded.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endif %}

<!-- Room Availability Overview -->
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
                            <span class="badge badge-booked">Occupied</span>
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

<!-- Bookings List -->
<div class="card border-0 shadow-sm">
    <div class="card-header bg-dark text-white d-flex justify-content-between align-items-center">
        <span class="fw-bold">Reservations List</span>
        {% if is_admin %}
        <span class="badge bg-warning text-dark">Admin Controls Enabled</span>
        {% endif %}
    </div>
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
                        <th>Status</th>
                        {% if is_admin %}
                        <th>Admin Action</th>
                        {% endif %}
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
                        <td>
                            {% if b[6] == 'Checked In' %}
                            <span class="badge bg-success">Checked In</span>
                            {% elif b[6] == 'Checked Out' %}
                            <span class="badge bg-secondary">Checked Out</span>
                            {% else %}
                            <span class="badge bg-warning text-dark">Booked</span>
                            {% endif %}
                        </td>
                        {% if is_admin %}
                        <td>
                            {% if b[6] == 'Booked' %}
                            <a href="/checkin/{{ b[0] }}" class="btn btn-success btn-sm py-0">Check In</a>
                            {% elif b[6] == 'Checked In' %}
                            <a href="/checkout/{{ b[0] }}" class="btn btn-danger btn-sm py-0">Check Out</a>
                            {% else %}
                            <span class="text-muted small">Completed</span>
                            {% endif %}
                        </td>
                        {% endif %}
                    </tr>
                    {% else %}
                    <tr>
                        <td colspan="7" class="text-center text-muted p-3">No bookings recorded yet.</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
"""

# Render Helper
def render_page(content, **context):
    full_template = BASE_LAYOUT.replace("BODY_CONTENT", content)
    return render_template_string(full_template, is_admin=is_admin_user(), **context)

# Routes
@app.route('/')
def home():
    init_db()
    return render_page(HOME_CONTENT, active_page='home')

@app.route('/guest_login')
def guest_login():
    init_db()
    session['username'] = 'Guest_User'
    log_user_session('Guest_User')
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    init_db()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect("hotel_enterprise.db")
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, 0)", (username, password))
            conn.commit()
            conn.close()
            session['username'] = username
            log_user_session(username)
            return redirect(url_for('home'))
        except sqlite3.IntegrityError:
            conn.close()
            return render_page(REGISTER_CONTENT, active_page='register', error="Username already exists!")
            
    return render_page(REGISTER_CONTENT, active_page='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    init_db()
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = sqlite3.connect("hotel_enterprise.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            log_user_session(username)
            return redirect(url_for('home'))
        else:
            return render_page(LOGIN_CONTENT, active_page='login', error="Invalid username or password")
            
    return render_page(LOGIN_CONTENT, active_page='login')

@app.route('/logout')
def logout():
    if 'username' in session:
        clear_user_session(session['username'])
        session.pop('username', None)
    return redirect(url_for('home'))

@app.route('/rooms')
def rooms():
    return render_page(ROOMS_CONTENT, rooms=ROOMS_DATA, active_page='rooms')

@app.route('/book_page')
def book_page():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    selected_room = request.args.get('room', '')
    return render_page(BOOKING_CONTENT, rooms=ROOMS_DATA, selected_room=selected_room, active_page='book')

@app.route('/book', methods=['POST'])
def book():
    if 'username' not in session:
        return redirect(url_for('login'))
        
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
    cursor.execute("INSERT INTO bookings (guest_name, room_type, nights, meal_plan, total_price, status) VALUES (?, ?, ?, ?, ?, 'Booked')",
                   (guest_name, room_type, nights, meal_plan, total_price))
    conn.commit()
    conn.close()
    
    return redirect(url_for('status'))

@app.route('/checkin/<int:booking_id>')
def checkin(booking_id):
    if not is_admin_user():
        return redirect(url_for('login'))
        
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = 'Checked In' WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('status'))

@app.route('/checkout/<int:booking_id>')
def checkout(booking_id):
    if not is_admin_user():
        return redirect(url_for('login'))
        
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE bookings SET status = 'Checked Out' WHERE id = ?", (booking_id,))
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
    
    # Retrieve active user sessions for Admin view
    cursor.execute("SELECT * FROM active_sessions ORDER BY id DESC")
    active_users = cursor.fetchall()
    
    conn.close()
    
    occupied_room_names = [b[2] for b in bookings if b[6] in ('Booked', 'Checked In')]
    availability = []
    for r in ROOMS_DATA:
        availability.append({
            "name": r["name"],
            "price": r["price"],
            "is_booked": r["name"] in occupied_room_names
        })
        
    return render_page(STATUS_CONTENT, bookings=bookings, availability=availability, active_users=active_users, active_page='status')

if __name__ == '__main__':
    app.run(debug=True)
