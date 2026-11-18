
import os
from pathlib import Path

import psycopg2
from dotenv import load_dotenv


# ============================================
# ENVIRONMENT CONFIGURATION
# ============================================

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")


# ============================================
# DATABASE CONNECTION
# ============================================

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5
    )


# ============================================
# DATABASE INITIALIZATION
# ============================================

def init_db():

    conn = None

    try:
        conn = get_db()

        with conn.cursor() as cur:

            # Create tables
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(150) UNIQUE NOT NULL,
                    password TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(150) NOT NULL,
                    description TEXT,
                    price NUMERIC(10,2) NOT NULL CHECK (price >= 0),
                    image TEXT
                );

                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id),
                    customer_name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    address TEXT NOT NULL,
                    payment_method VARCHAR(30) NOT NULL,
                    total NUMERIC(10,2) NOT NULL CHECK (total >= 0),
                    status VARCHAR(30) NOT NULL DEFAULT 'Pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS order_items (
                    id SERIAL PRIMARY KEY,
                    order_id INTEGER NOT NULL REFERENCES orders(id),
                    product_id INTEGER NOT NULL REFERENCES products(id),
                    quantity INTEGER NOT NULL CHECK (quantity > 0),
                    price NUMERIC(10,2) NOT NULL CHECK (price >= 0)
                );
            """)

            # Support existing databases created before status was added
            cur.execute("""
                ALTER TABLE orders
                ADD COLUMN IF NOT EXISTS status VARCHAR(30)
                NOT NULL DEFAULT 'Pending';
            """)

            # Check whether products already exist
            cur.execute("SELECT COUNT(*) FROM products")

            product_count = cur.fetchone()[0]

            # Insert sample products only once
            if product_count == 0:

                products = [
                    (
                        "Headphones",
                        "Wireless headphones",
                        2499,
                        "/images/products/headphones.jpg"
                    ),
                    (
                        "Smart Watch",
                        "Fitness smart watch",
                        3999,
                        "/images/products/smart-watch.jpg"
                    ),
                    (
                        "Backpack",
                        "Laptop backpack",
                        1499,
                        "/images/products/backpack.jpg"
                    ),
                    (
                        "Wireless Mouse",
                        "Ergonomic mouse",
                        899,
                        "/images/products/mouse.jpg"
                    ),
                    (
                        "Keyboard",
                        "Mechanical keyboard",
                        2999,
                        "/images/products/keyboard.jpg"
                    ),
                    (
                        "Running Shoes",
                        "Comfortable running shoes",
                        2199,
                        "/images/products/shoes.jpg"
                    )
                ]

                cur.executemany("""
                    INSERT INTO products (
                        name,
                        description,
                        price,
                        image
                    )
                    VALUES (%s, %s, %s, %s)
                """, products)

        conn.commit()

        print("Database initialized successfully.")

    except Exception:
        if conn:
            conn.rollback()

        raise

    finally:
        if conn:
            conn.close()
