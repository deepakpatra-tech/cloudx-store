
import os
from pathlib import Path
from decimal import Decimal

from dotenv import load_dotenv

from flask import (
    Flask,
    request,
    jsonify,
    session,
    send_from_directory
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from db import get_db, init_db


# ============================================
# APPLICATION CONFIGURATION
# ============================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

FRONTEND_DIR = str(
    (BASE_DIR.parent / "frontend").resolve()
)

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing")

app = Flask(__name__)

app.secret_key = SECRET_KEY

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.getenv(
        "COOKIE_SECURE", "false"
    ).lower() == "true"
)


# ============================================
# FRONTEND ROUTES
# ============================================

@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# ============================================
# REGISTER
# ============================================

@app.route("/api/register", methods=["POST"])
def register():

    data = request.get_json(silent=True) or {}

    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")

    if not isinstance(name, str) or not isinstance(email, str):
        return jsonify({"error": "Invalid input"}), 400

    if not isinstance(password, str):
        return jsonify({"error": "Invalid password"}), 400

    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return jsonify({
            "error": "All fields are required"
        }), 400

    if len(name) < 2 or len(name) > 100:
        return jsonify({
            "error": "Name must contain 2 to 100 characters"
        }), 400

    if len(email) > 150:
        return jsonify({
            "error": "Email is too long"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    conn = None

    try:
        conn = get_db()

        with conn.cursor() as cur:

            hashed_password = generate_password_hash(password)

            cur.execute("""
                INSERT INTO users (name, email, password)
                VALUES (%s, %s, %s)
                RETURNING id, name, email
            """, (name, email, hashed_password))

            user = cur.fetchone()

        conn.commit()

        return jsonify({
            "message": "Registration successful",
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2]
            }
        }), 201

    except Exception as error:

        if conn:
            conn.rollback()

        if getattr(error, "pgcode", None) == "23505":
            return jsonify({
                "error": "Email already registered"
            }), 409

        app.logger.exception("Registration failed")

        return jsonify({
            "error": "Registration failed"
        }), 500

    finally:
        if conn:
            conn.close()


# ============================================
# LOGIN
# ============================================

@app.route("/api/login", methods=["POST"])
def login():

    data = request.get_json(silent=True) or {}

    email = data.get("email", "")
    password = data.get("password", "")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({"error": "Invalid input"}), 400

    email = email.strip().lower()

    if not email or not password:
        return jsonify({
            "error": "Email and password are required"
        }), 400

    conn = None

    try:
        conn = get_db()

        with conn.cursor() as cur:

            cur.execute("""
                SELECT id, name, email, password
                FROM users
                WHERE email = %s
            """, (email,))

            user = cur.fetchone()

        if not user or not check_password_hash(user[3], password):
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        session.clear()
        session["user_id"] = user[0]

        return jsonify({
            "message": "Login successful",
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2]
            }
        })

    except Exception:

        app.logger.exception("Login failed")

        return jsonify({
            "error": "Unable to login"
        }), 500

    finally:
        if conn:
            conn.close()


# ============================================
# CHECK LOGIN SESSION
# ============================================

@app.route("/api/session", methods=["GET"])
def check_session():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "Not logged in"
        }), 401

    conn = None

    try:
        conn = get_db()

        with conn.cursor() as cur:

            cur.execute("""
                SELECT id, name, email
                FROM users
                WHERE id = %s
            """, (user_id,))

            user = cur.fetchone()

        if not user:
            session.clear()

            return jsonify({
                "error": "User not found"
            }), 401

        return jsonify({
            "user": {
                "id": user[0],
                "name": user[1],
                "email": user[2]
            }
        })

    except Exception:

        app.logger.exception("Session verification failed")

        return jsonify({
            "error": "Unable to verify session"
        }), 500

    finally:
        if conn:
            conn.close()


# ============================================
# LOGOUT
# ============================================

@app.route("/api/logout", methods=["POST"])
def logout():

    session.clear()

    return jsonify({
        "message": "Logged out successfully"
    })


# ============================================
# GET PRODUCTS
# ============================================

@app.route("/api/products", methods=["GET"])
def products():

    conn = None

    try:
        conn = get_db()

        with conn.cursor() as cur:

            cur.execute("""
                SELECT id, name, description, price, image
                FROM products
                ORDER BY id
            """)

            rows = cur.fetchall()

        result = [
            {
                "id": row[0],
                "name": row[1],
                "description": row[2],
                "price": float(row[3]),
                "image": row[4]
            }
            for row in rows
        ]

        return jsonify(result)

    except Exception:

        app.logger.exception("Unable to load products")

        return jsonify({
            "error": "Unable to load products"
        }), 500

    finally:
        if conn:
            conn.close()


# ============================================
# PLACE ORDER
# ============================================

@app.route("/api/orders", methods=["POST"])
def place_order():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    data = request.get_json(silent=True) or {}

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request"}), 400

    items = data.get("items", [])
    name = data.get("customer_name", "")
    phone = data.get("phone", "")
    address = data.get("address", "")
    payment_method = data.get("payment_method", "COD")

    if not all(isinstance(value, str) for value in [
        name, phone, address, payment_method
    ]):
        return jsonify({"error": "Invalid customer details"}), 400

    name = name.strip()
    phone = phone.strip()
    address = address.strip()

    if not name or not phone or not address:
        return jsonify({
            "error": "Customer details are required"
        }), 400

    if len(name) > 100 or len(address) > 2000:
        return jsonify({
            "error": "Customer details are too long"
        }), 400

    if not phone.isdigit() or len(phone) != 10:
        return jsonify({
            "error": "Enter a valid 10-digit phone number"
        }), 400

    if payment_method != "COD":
        return jsonify({
            "error": "Only Cash on Delivery is supported"
        }), 400

    if not isinstance(items, list) or not items or len(items) > 50:
        return jsonify({
            "error": "Invalid or empty cart"
        }), 400

    conn = None

    try:
        conn = get_db()

        with conn.cursor() as cur:

            subtotal = Decimal("0.00")
            validated_items = []

            for item in items:

                if not isinstance(item, dict):
                    raise ValueError("Invalid cart item")

                product_id = item.get("product_id")
                quantity = item.get("quantity")

                if type(product_id) is not int or product_id <= 0:
                    raise ValueError("Invalid product ID")

                if type(quantity) is not int or not 1 <= quantity <= 100:
                    raise ValueError("Invalid quantity")

                cur.execute("""
                    SELECT id, price
                    FROM products
                    WHERE id = %s
                """, (product_id,))

                product = cur.fetchone()

                if not product:
                    raise ValueError("Product not found")

                price = Decimal(str(product[1]))

                subtotal += price * quantity

                validated_items.append((
                    product_id,
                    quantity,
                    price
                ))

            shipping = Decimal("50.00")
            total = subtotal + shipping

            cur.execute("""
                INSERT INTO orders (
                    user_id,
                    customer_name,
                    phone,
                    address,
                    payment_method,
                    total
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_id,
                name,
                phone,
                address,
                payment_method,
                total
            ))

            order_id = cur.fetchone()[0]

            for product_id, quantity, price in validated_items:

                cur.execute("""
                    INSERT INTO order_items (
                        order_id,
                        product_id,
                        quantity,
                        price
                    )
                    VALUES (%s, %s, %s, %s)
                """, (
                    order_id,
                    product_id,
                    quantity,
                    price
                ))

        conn.commit()

        return jsonify({
            "message": "Order placed successfully",
            "order_id": order_id,
            "total": float(total)
        }), 201

    except (ValueError, TypeError) as error:

        if conn:
            conn.rollback()

        return jsonify({
            "error": str(error)
        }), 400

    except Exception:

        if conn:
            conn.rollback()

        app.logger.exception("Order placement failed")

        return jsonify({
            "error": "Unable to place order"
        }), 500

    finally:
        if conn:
            conn.close()


# ============================================
# MY ORDERS
# ============================================

@app.route("/api/my-orders", methods=["GET"])
def my_orders():

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "error": "Please login first"
        }), 401

    conn = None

    try:
        conn = get_db()

        with conn.cursor() as cur:

            cur.execute("""
                SELECT
                    o.id,
                    o.customer_name,
                    o.phone,
                    o.address,
                    o.payment_method,
                    o.total,
                    o.status,
                    o.created_at,
                    oi.product_id,
                    p.name,
                    p.image,
                    oi.quantity,
                    oi.price
                FROM orders o
                LEFT JOIN order_items oi
                    ON o.id = oi.order_id
                LEFT JOIN products p
                    ON oi.product_id = p.id
                WHERE o.user_id = %s
                ORDER BY o.created_at DESC, o.id DESC
            """, (user_id,))

            rows = cur.fetchall()

        orders = {}

        for row in rows:

            order_id = row[0]

            if order_id not in orders:

                orders[order_id] = {
                    "order_id": order_id,
                    "customer_name": row[1],
                    "phone": row[2],
                    "address": row[3],
                    "payment_method": row[4],
                    "total": float(row[5]),
                    "status": row[6],
                    "created_at": (
                        row[7].isoformat()
                        if row[7] else None
                    ),
                    "items": []
                }

            if row[8] is not None:

                orders[order_id]["items"].append({
                    "product_id": row[8],
                    "name": row[9],
                    "image": row[10],
                    "quantity": row[11],
                    "price": float(row[12])
                })

        return jsonify({
            "orders": list(orders.values())
        })

    except Exception:

        app.logger.exception("Unable to load customer orders")

        return jsonify({
            "error": "Unable to load orders"
        }), 500

    finally:
        if conn:
            conn.close()


# ============================================
# DATABASE HEALTH CHECK
# ============================================

@app.route("/api/health", methods=["GET"])
def health():

    conn = None

    try:
        conn = get_db()

        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.fetchone()

        return jsonify({
            "status": "healthy",
            "database": "connected"
        })

    except Exception:

        app.logger.exception("Database health check failed")

        return jsonify({
            "status": "unhealthy",
            "database": "disconnected"
        }), 500

    finally:
        if conn:
            conn.close()


# ============================================
# LOCAL DEVELOPMENT STARTUP
# ============================================

# ============================================
# DATABASE INITIALIZATION
# ============================================

init_db()
