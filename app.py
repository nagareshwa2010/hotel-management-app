import os
from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nr_hotel_secret_key_for_demo")

# Database Initialization
def init_db():
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    
    # Bookings Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT NOT NULL,
            room_type TEXT NOT NULL,
            nights INTEGER NOT NULL,
            total_price INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Full HTML & CSS Template with Updated Hotel Name: NR Hotel
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NR Hotel - 5 Star Luxury Management</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&family=Playfair+Display:wght@700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Poppins', sans-serif; background-color: #f8f9fa; }
        h1, h2, h3, .navbar-brand { font-family: 'Playfair Display', serif; }
        .navbar { background-color: #0b132b !important; }
        .navbar-brand, .nav-link { color: #d4af37 !important; }
        .hero-section {
            background: linear-gradient(rgba(11, 19, 43, 0.75), rgba(11, 19, 43, 0.75)), 
                        url('https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1350&q=80');
            background-size: cover; background-position: center;
            color: white; padding: 80px 0; text-align: center;
        }
        .card-room {
            border: none; border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .card-room:hover { transform: translateY(-5px); }
        .price-tag { color: #d4af37; font-weight: 600; font-size: 1.2rem; }
        .btn-gold { background-color: #d4af37; color: #0b132b; font-weight: 600; border: none; }
        .btn-gold:hover { background-color: #b59226; color: white; }
    </style>
</head>
<body>

    <!-- Navbar -->
    <nav class="navbar navbar-expand-lg navbar-dark sticky-top">
        <div class="container">
            <a class="navbar-brand fs-3" href="/">🏰 NR Hotel</a>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link active" href="/">Home</a></li>
                    <li class="nav-item"><a class="nav-link" href="#rooms">Rooms & Suites</a></li>
                    <li class="nav-item"><a class="nav-link" href="#book">Book Now</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Banner -->
    <div class="hero-section">
        <div class="container">
            <h1 class="display-3 fw-bold">NR Hotel & Suites</h1>
            <p class="lead">Luxury Stay & World-Class Hospitality</p>
            <a href="#rooms" class="btn btn-gold btn-lg mt-3">Explore All Rooms</a>
        </div>
    </div>

    <!-- Rooms Section (6 Rooms) -->
    <div class="container my-5" id="rooms">
        <h2 class="text-center mb-4 text-dark">Our Rooms & Luxury Suites</h2>
        <div class="row g-4">
            
            <!-- 1. Standard Room -->
            <div class="col-md-4">
                <div class="card card-room h-100">
                    <img src="https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=500&q=80" class="card-img-top" alt="Standard Room" style="height: 200px; object-fit: cover; border-radius: 15px 15px 0 0;">
                    <div class="card-body">
                        <h4 class="card-title">Standard Room</h4>
                        <p class="card-text text-muted">Cozy queen bed, AC, Free Wi-Fi, and Work desk.</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="price-tag">₹2,000 / night</span>
                            <a href="#book" class="btn btn-gold btn-sm">Book</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 2. Deluxe Suite -->
            <div class="col-md-4">
                <div class="card card-room h-100">
                    <img src="https://images.unsplash.com/photo-1611892440504-42a792e24d32?auto=format&fit=crop&w=500&q=80" class="card-img-top" alt="Deluxe Room" style="height: 200px; object-fit: cover; border-radius: 15px 15px 0 0;">
                    <div class="card-body">
                        <h4 class="card-title">Deluxe Suite</h4>
                        <p class="card-text text-muted">King size bed, Ocean view, Free Wi-Fi, and Breakfast.</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="price-tag">₹5,000 / night</span>
                            <a href="#book" class="btn btn-gold btn-sm">Book</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 3. Executive Suite -->
            <div class="col-md-4">
                <div class="card card-room h-100">
                    <img src="https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=500&q=80" class="card-img-top" alt="Executive Room" style="height: 200px; object-fit: cover; border-radius: 15px 15px 0 0;">
                    <div class="card-body">
                        <h4 class="card-title">Executive Suite</h4>
                        <p class="card-text text-muted">Private balcony, Jacuzzi, Mini-bar, Room Service.</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="price-tag">₹8,000 / night</span>
                            <a href="#book" class="btn btn-gold btn-sm">Book</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 4. Family Suite -->
            <div class="col-md-4">
                <div class="card card-room h-100">
                    <img src="https://images.unsplash.com/photo-1596394516093-501ba68a0ba6?auto=format&fit=crop&w=500&q=80" class="card-img-top" alt="Family Suite" style="height: 200px; object-fit: cover; border-radius: 15px 15px 0 0;">
                    <div class="card-body">
                        <h4 class="card-title">Family Suite</h4>
                        <p class="card-text text-muted">Spacious room with 2 King beds, living space, and kids area access.</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="price-tag">₹10,000 / night</span>
                            <a href="#book" class="btn btn-gold btn-sm">Book</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 5. Presidential Suite -->
            <div class="col-md-4">
                <div class="card card-room h-100">
                    <img src="https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=500&q=80" class="card-img-top" alt="Presidential Room" style="height: 200px; object-fit: cover; border-radius: 15px 15px 0 0;">
                    <div class="card-body">
                        <h4 class="card-title">Presidential Suite</h4>
                        <p class="card-text text-muted">Penthouse view, Private pool, Personal Butler service.</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="price-tag">₹15,000 / night</span>
                            <a href="#book" class="btn btn-gold btn-sm">Book</a>
                        </div>
                    </div>
                </div>
            </div>

            <!-- 6. Penthouse Suite -->
            <div class="col-md-4">
                <div class="card card-room h-100">
                    <img src="https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=500&q=80" class="card-img-top" alt="Penthouse Suite" style="height: 200px; object-fit: cover; border-radius: 15px 15px 0 0;">
                    <div class="card-body">
                        <h4 class="card-title">Penthouse Suite</h4>
                        <p class="card-text text-muted">Top floor panoramic city view, private terrace, and plunge pool.</p>
                        <div class="d-flex justify-content-between align-items-center mt-3">
                            <span class="price-tag">₹20,000 / night</span>
                            <a href="#book" class="btn btn-gold btn-sm">Book</a>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>

    <!-- Booking Form Section -->
    <div class="container my-5 p-4 bg-white rounded-3 shadow-sm" id="book" style="max-width: 600px;">
        <h3 class="text-center mb-3">Quick Reservation</h3>
        <form action="/book" method="POST">
            <div class="mb-3">
                <label class="form-label">Guest Name</label>
                <input type="text" name="guest_name" class="form-control" placeholder="Enter your full name" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Select Room Type</label>
                <select name="room_type" class="form-select">
                    <option value="Standard Room - ₹2000">Standard Room - ₹2,000</option>
                    <option value="Deluxe Suite - ₹5000">Deluxe Suite - ₹5,000</option>
                    <option value="Executive Suite - ₹8000">Executive Suite - ₹8,000</option>
                    <option value="Family Suite - ₹10000">Family Suite - ₹10,000</option>
                    <option value="Presidential Suite - ₹15000">Presidential Suite - ₹15,000</option>
                    <option value="Penthouse Suite - ₹20000">Penthouse Suite - ₹20,000</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Number of Nights</label>
                <input type="number" name="nights" class="form-control" min="1" value="1" required>
            </div>
            <button type="submit" class="btn btn-gold w-100">Confirm Booking</button>
        </form>
    </div>

    <!-- Recent Bookings Display -->
    {% if bookings %}
    <div class="container my-5">
        <h3 class="text-center mb-3">Recent Reservations</h3>
        <div class="table-responsive">
            <table class="table table-striped table-hover shadow-sm">
                <thead class="table-dark">
                    <tr>
                        <th>#</th>
                        <th>Guest Name</th>
                        <th>Room Type</th>
                        <th>Nights</th>
                        <th>Total Amount</th>
                    </tr>
                </thead>
                <tbody>
                    {% for booking in bookings %}
                    <tr>
                        <td>{{ booking[0] }}</td>
                        <td>{{ booking[1] }}</td>
                        <td>{{ booking[2] }}</td>
                        <td>{{ booking[3] }}</td>
                        <td>₹{{ booking[4] }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% endif %}

</body>
</html>
"""

@app.route('/')
def home():
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY id DESC LIMIT 5")
    bookings = cursor.fetchall()
    conn.close()
    return render_template_string(HTML_TEMPLATE, bookings=bookings)

@app.route('/book', methods=['POST'])
def book():
    guest_name = request.form.get('guest_name')
    room_type_info = request.form.get('room_type')
    nights = int(request.form.get('nights', 1))
    
    # Pricing Dictionary
    price_map = {
        "Standard Room - ₹2000": 2000,
        "Deluxe Suite - ₹5000": 5000,
        "Executive Suite - ₹8000": 8000,
        "Family Suite - ₹10000": 10000,
        "Presidential Suite - ₹15000": 15000,
        "Penthouse Suite - ₹20000": 20000
    }
    price_per_night = price_map.get(room_type_info, 2000)
    total_price = price_per_night * nights
    
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bookings (guest_name, room_type, nights, total_price) VALUES (?, ?, ?, ?)",
                   (guest_name, room_type_info.split(" - ")[0], nights, total_price))
    conn.commit()
    conn.close()
    
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
