import os
from flask import Flask, request, render_template_string, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "5star_hotel_secret_key_for_demo")

MEAL_PLANS = {
    "EP (Room Only)": 0,
    "CP (Room + Breakfast)": 800,
    "MAP (Room + Breakfast + Dinner)": 1800,
    "AP (Room + All Meals)": 2800
}

def init_db():
    conn = sqlite3.connect("hotel_enterprise.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            room_number INTEGER PRIMARY KEY,
            category TEXT,
            price_per_night REAL,
            status TEXT DEFAULT 'Available',
            guest_name TEXT DEFAULT '',
            meal_plan TEXT DEFAULT 'EP (Room Only)'
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS service_bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guest_name TEXT,
            service_type TEXT,
            booking_date TEXT,
            status TEXT DEFAULT 'Confirmed'
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'Admin')")
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('guest', 'guest123', 'Guest')")

    cursor.execute("SELECT COUNT(*) FROM rooms")
    if cursor.fetchone()[0] == 0:
        default_rooms = [
            (101, 'Deluxe Room', 5000, 'Available', '', 'EP (Room Only)'),
            (102, 'Deluxe Room', 5000, 'Available', '', 'EP (Room Only)'),
            (201, 'Super Deluxe', 8500, 'Available', '', 'EP (Room Only)'),
            (202, 'Super Deluxe', 8500, 'Available', '', 'EP (Room Only)'),
            (301, 'Executive Suite', 15000, 'Available', '', 'EP (Room Only)'),
            (501, 'Presidential Suite', 35000, 'Available', '', 'EP (Room Only)')
        ]
        cursor.executemany("INSERT INTO rooms VALUES (?, ?, ?, ?, ?, ?)", default_rooms)

    conn.commit()
    conn.close()

init_db()

def get_db():
    return sqlite3.connect("hotel_enterprise.db")

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT username, role FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()
        
        if user:
            session['username'] = user[0]
            session['role'] = user[1]
            return redirect(url_for('dashboard'))
        else:
            error = "தவறான பயனர் பெயர் அல்லது கடவுச்சொல்!"

    login_html = """
    <!DOCTYPE html>
    <html lang="ta">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Grand Palace Portal</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); height: 100vh; margin: 0; display: flex; justify-content: center; align-items: center; color: white; }
            .login-card { background: rgba(255, 255, 255, 0.12); backdrop-filter: blur(12px); padding: 25px; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.37); width: 85%; max-width: 340px; text-align: center; border: 1px solid rgba(255,255,255,0.18); }
            h2 { margin-bottom: 5px; color: #f1c40f; font-size: 24px; }
            p { font-size: 13px; margin-bottom: 20px; color: #e0e0e0; }
            input[type="text"], input[type="password"] { width: 100%; box-sizing: border-box; padding: 14px; margin: 8px 0; border: none; border-radius: 8px; background: rgba(255,255,255,0.95); font-size: 15px; }
            input[type="submit"] { width: 100%; padding: 14px; border: none; border-radius: 8px; background: #f1c40f; color: #1a252f; font-weight: bold; font-size: 16px; cursor: pointer; margin-top: 12px; }
            .demo-info { font-size: 11px; margin-top: 18px; background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; text-align: left; line-height: 1.5; }
            .error { color: #ff6b6b; margin-top: 10px; font-weight: bold; font-size: 13px; }
        </style>
    </head>
    <body>
        <div class="login-card">
            <h2>👑 Grand Palace</h2>
            <p>5-Star Cloud Hotel Management System</p>
            <form method="POST">
                <input type="text" name="username" placeholder="Username" required><br>
                <input type="password" name="password" placeholder="Password" required><br>
                <input type="submit" value="Sign In">
            </form>
            {% if error %}
                <div class="error">{{ error }}</div>
            {% endif %}
            <div class="demo-info">
                <strong>Live Credentials:</strong><br>
                🔑 Admin: admin / admin123<br>
                🔑 Guest: guest / guest123
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(login_html, error=error)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))

    user_role = session.get('role')
    username = session.get('username')
    message = None
    bill_data = None

    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "book_room":
            room_num = int(request.form.get("room_num"))
            guest_name = request.form.get("guest_name")
            selected_meal = request.form.get("meal_plan")
            
            cursor.execute("SELECT status FROM rooms WHERE room_number=?", (room_num,))
            room = cursor.fetchone()
            if room and room[0] == 'Available':
                cursor.execute("UPDATE rooms SET status='Booked', guest_name=?, meal_plan=? WHERE room_number=?", (guest_name, selected_meal, room_num))
                conn.commit()
                message = f"வெற்றி: அறை {room_num} ({guest_name})-க்கு {selected_meal} திட்டத்துடன் ஒதுக்கப்பட்டது!"
            else:
                message = "தவறு: இந்த அறை ஏற்கனவே முன்பதிவு செய்யப்பட்டுள்ளது."

        elif action == "checkout_room":
            room_num = int(request.form.get("checkout_num"))
            nights = int(request.form.get("nights"))
            
            cursor.execute("SELECT room_number, category, price_per_night, guest_name, status, meal_plan FROM rooms WHERE room_number=?", (room_num,))
            room = cursor.fetchone()
            
            if room and room[4] == 'Booked':
                room_price = room[2]
                meal_plan_name = room[5]
                meal_price = MEAL_PLANS.get(meal_plan_name, 0)
                
                room_total = room_price * nights
                meal_total = meal_price * nights
                subtotal = room_total + meal_total
                
                gst_tax = subtotal * 0.18
                grand_total = subtotal + gst_tax
                
                bill_data = {
                    "room_num": room[0],
                    "category": room[1],
                    "guest_name": room[3],
                    "meal_plan": meal_plan_name,
                    "nights": nights,
                    "room_total": f"₹{room_total:,.2f}",
                    "meal_total": f"₹{meal_total:,.2f}",
                    "subtotal": f"₹{subtotal:,.2f}",
                    "gst_tax": f"₹{gst_tax:,.2f}",
                    "grand_total": f"₹{grand_total:,.2f}"
                }
                
                cursor.execute("UPDATE rooms SET status='Available', guest_name='', meal_plan='EP (Room Only)' WHERE room_number=?", (room_num,))
                conn.commit()
                message = f"அறை {room_num} காலி செய்யப்பட்டது (Check-out Complete)."
            else:
                message = "தவறு: அறை செல்லுபடியற்றது."

        elif action == "book_service":
            service_type = request.form.get("service_type")
            b_date = request.form.get("b_date")
            cursor.execute("INSERT INTO service_bookings (guest_name, service_type, booking_date) VALUES (?, ?, ?)", (username, service_type, b_date))
            conn.commit()
            message = f"வெற்றி: {service_type} சேவை {b_date} தேதியில் உறுதிசெய்யப்பட்டது!"

    cursor.execute("SELECT * FROM rooms")
    rooms_data = cursor.fetchall()

    cursor.execute("SELECT * FROM service_bookings")
    service_data = cursor.fetchall()

    conn.close()

    dashboard_html = """
    <!DOCTYPE html>
    <html lang="ta">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Grand Palace Dashboard</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f0f2f5; margin: 0; padding: 0; }
            .header { background: #1a252f; color: white; padding: 15px 20px; display: flex; flex-direction: column; gap: 8px; border-bottom: 4px solid #f1c40f; }
            .header h1 { margin: 0; font-size: 18px; color: #f1c40f; }
            .user-bar { display: flex; justify-content: space-between; align-items: center; font-size: 13px; }
            .logout-btn { background: #e74c3c; color: white; padding: 5px 10px; text-decoration: none; border-radius: 4px; font-weight: bold; font-size: 12px; }
            .container { padding: 15px; }
            .card { background: white; padding: 18px; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); margin-bottom: 15px; }
            h3 { color: #1a252f; border-bottom: 2px solid #f1c40f; padding-bottom: 6px; margin-top: 0; font-size: 16px; }
            input[type="text"], input[type="number"], input[type="date"], select { width: 100%; box-sizing: border-box; padding: 12px; margin: 6px 0 12px 0; border: 1px solid #ccc; border-radius: 8px; font-size: 14px; }
            input[type="submit"] { width: 100%; padding: 13px; background: #27ae60; color: white; border: none; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 15px; }
            .btn-checkout { background: #e74c3c !important; }
            .status-tag { padding: 3px 6px; border-radius: 10px; font-size: 10px; font-weight: bold; color: white; display: inline-block; }
            .bg-available { background: #2ecc71; }
            .bg-booked { background: #e74c3c; }
            .message-box { background: #d4edda; color: #155724; padding: 10px; border-radius: 8px; margin-bottom: 15px; border-left: 4px solid #28a745; font-size: 13px; text-align: center; }
            .bill-receipt { background: #fffde7; border: 1px dashed #f1c40f; padding: 12px; border-radius: 8px; margin-top: 12px; font-size: 12px; }
            .table-wrapper { overflow-x: auto; }
            .room-table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 11px; }
            .room-table th, .room-table td { padding: 8px 4px; border-bottom: 1px solid #eee; text-align: left; }
        </style>
    </head>
    <body>

        <div class="header">
            <h1>👑 Grand Palace Portal</h1>
            <div class="user-bar">
                <span>User: <b>{{ username }}</b> ({{ user_role }})</span>
                <a href="/logout" class="logout-btn">Logout</a>
            </div>
        </div>

        <div class="container">
            {% if message %}
                <div class="message-box">{{ message }}</div>
            {% endif %}

            <div class="card">
                <h3>🏨 Rooms & Meal Plans</h3>
                <div class="table-wrapper">
                    <table class="room-table">
                        <tr>
                            <th>Room</th>
                            <th>Category</th>
                            <th>Price</th>
                            <th>Meal Plan</th>
                            <th>Status</th>
                        </tr>
                        {% for r_num, cat, price, status, g_name, meal in rooms_data %}
                        <tr>
                            <td><b>{{ r_num }}</b></td>
                            <td>{{ cat }}</td>
                            <td>₹{{ "{:,.0f}".format(price) }}</td>
                            <td>{{ meal }}</td>
                            <td>
                                {% if status == 'Available' %}
                                    <span class="status-tag bg-available">Free</span>
                                {% else %}
                                    <span class="status-tag bg-booked">{{ g_name }}</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </table>
                </div>
            </div>

            {% if user_role == 'Admin' %}
            <div class="card">
                <h3>🛎️ Check-In</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="book_room">
                    <input type="number" name="room_num" placeholder="Room Number (e.g. 101)" required>
                    <input type="text" name="guest_name" placeholder="Guest Full Name" required>
                    
                    <label style="font-size: 11px; font-weight: bold;">Meal Package:</label>
                    <select name="meal_plan" required>
                        {% for plan, rate in meal_plans.items() %}
                            <option value="{{ plan }}">{{ plan }} (+₹{{ rate }})</option>
                        {% endfor %}
                    </select>

                    <input type="submit" value="Confirm Check-In">
                </form>
            </div>

            <div class="card">
                <h3>🧾 Check-Out & Bill</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="checkout_room">
                    <input type="number" name="checkout_num" placeholder="Room Number" required>
                    <input type="number" name="nights" placeholder="Nights Stayed" required>
                    <input type="submit" value="Check-Out & Invoice" class="btn-checkout">
                </form>

                {% if bill_data %}
                <div class="bill-receipt">
                    <h4 style="margin:0 0 8px 0; color:#b7950b;">🧾 Tax Invoice</h4>
                    Guest: <b>{{ bill_data.guest_name }}</b><br>
                    Room: <b>{{ bill_data.room_num }} ({{ bill_data.category }})</b><br>
                    Plan: <b>{{ bill_data.meal_plan }}</b><br>
                    Nights: <b>{{ bill_data.nights }}</b><hr>
                    Room Charges: {{ bill_data.room_total }}<br>
                    Meal Charges: {{ bill_data.meal_total }}<br>
                    Subtotal: {{ bill_data.subtotal }}<br>
                    GST (18%): {{ bill_data.gst_tax }}<br>
                    <h4 style="margin:5px 0 0 0; color:#27ae60;">Total: {{ bill_data.grand_total }}</h4>
                </div>
                {% endif %}
            </div>
            {% endif %}

            {% if user_role == 'Guest' or user_role == 'Admin' %}
            <div class="card">
                <h3>🍽️ Dining & Spa Booking</h3>
                <form method="POST">
                    <input type="hidden" name="action" value="book_service">
                    <select name="service_type" required>
                        <option value="">Select Service...</option>
                        <option value="Fine Dining Table">Fine Dining Table</option>
                        <option value="Luxury Spa & Massage">Luxury Spa & Massage</option>
                        <option value="Swimming Pool Cabana">Swimming Pool Cabana</option>
                    </select>
                    <input type="date" name="b_date" required>
                    <input type="submit" value="Book Service">
                </form>
            </div>
            {% endif %}

        </div>

    </body>
    </html>
    """
    return render_template_string(dashboard_html, username=username, user_role=user_role, rooms_data=rooms_data, service_data=service_data, message=message, bill_data=bill_data, meal_plans=MEAL_PLANS)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
