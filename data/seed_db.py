"""Seed script: creates and populates sole_syntax.db with 15 customers and orders."""
import os
import sqlite3
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "sole_syntax.db")


def get_date(days_ago: int) -> str:
    return (date.today() - timedelta(days=days_ago)).isoformat()


CUSTOMERS = [
    # id, name, email, phone, loyalty_tier, annual_spend
    (1,  "Alice Johnson",    "alice@email.com",    "555-0101", "Gold",     650.00),
    (2,  "Bob Martinez",     "bob@email.com",      "555-0102", "Standard", 120.00),
    (3,  "Carol White",      "carol@email.com",    "555-0103", "Platinum", 1250.00),
    (4,  "David Kim",        "david@email.com",    "555-0104", "Standard",  80.00),
    (5,  "Emma Davis",       "emma@email.com",     "555-0105", "Gold",     720.00),
    (6,  "Frank Thomas",     "frank@email.com",    "555-0106", "Standard", 200.00),
    (7,  "Grace Lee",        "grace@email.com",    "555-0107", "Standard",  45.00),
    (8,  "Henry Brown",      "henry@email.com",    "555-0108", "Standard", 310.00),
    (9,  "Isabella Garcia",  "isabella@email.com", "555-0109", "Gold",     580.00),
    (10, "James Wilson",     "james@email.com",    "555-0110", "Standard",  95.00),
    (11, "Karen Moore",      "karen@email.com",    "555-0111", "Standard", 160.00),
    (12, "Liam Taylor",      "liam@email.com",     "555-0112", "Platinum", 1800.00),
    (13, "Mia Anderson",     "mia@email.com",      "555-0113", "Standard",  55.00),
    (14, "Noah Jackson",     "noah@email.com",     "555-0114", "Standard", 230.00),
    (15, "Olivia Harris",    "olivia@email.com",   "555-0115", "Gold",     510.00),
]

ORDERS = [
    # id, customer_id, product, size, price, discount_pct, delivery_date, status, condition, has_receipt, is_defective
    ("ORD-001", 1,  "Air Stride Pro",        10,  129.99,  0,  get_date(20), "delivered", "unworn",  True,  False),  # Alice - valid refund (Gold, 20 days)
    ("ORD-002", 2,  "Classic Runner",         9,   89.99,  0,  get_date(45), "delivered", "worn",    True,  False),  # Bob - worn + 45 days (deny)
    ("ORD-003", 3,  "Urban Glide X",         11,  159.99,  0,  get_date(10), "delivered", "unworn",  True,  False),  # Carol - valid (Platinum)
    ("ORD-004", 4,  "Trail Blazer 2000",      8,   74.99, 25,  get_date(5),  "delivered", "unworn",  True,  False),  # David - FINAL SALE (deny)
    ("ORD-005", 5,  "Velocity Sprint",       10,  199.99,  0,  get_date(40), "delivered", "unworn",  True,  False),  # Emma - within Gold 45-day window
    ("ORD-006", 6,  "Canvas Daily",           9,   59.99,  0,  get_date(15), "delivered", "worn",    True,  False),  # Frank - worn (deny)
    ("ORD-007", 7,  "Night Racer Elite",      7,  149.99,  0,  get_date(12), "delivered", "unworn",  False, False),  # Grace - no receipt (deny)
    ("ORD-008", 8,  "Cloud Walker Pro",      12,  109.99,  0,  get_date(25), "delivered", "unworn",  True,  False),  # Henry - valid standard refund
    ("ORD-009", 9,  "Flex Runner",           10,   99.99,  0,  get_date(30), "delivered", "unworn",  True,  False),  # Isabella - exactly 30 days (edge, Gold 45-day = valid)
    ("ORD-010", 10, "Stealth Trainer",        9,  179.99,  0,  get_date(60), "delivered", "unworn",  True,  False),  # James - 60 days, standard (deny)
    ("ORD-011", 11, "Sole Signature Slip-On", 8,   49.99, 30,  get_date(3),  "delivered", "unworn",  True,  False),  # Karen - FINAL SALE 30% off (deny)
    ("ORD-012", 12, "Marathon Master",       11,  249.99,  0,  get_date(55), "delivered", "unworn",  True,  False),  # Liam - Platinum 60-day window (valid)
    ("ORD-013", 13, "Custom Kicks",          10,  300.00,  0,  get_date(8),  "delivered", "unworn",  True,  False),  # Mia - customized shoes (deny)
    ("ORD-014", 14, "Pavement Pounder",       9,  119.99,  0,  get_date(18), "delivered", "unworn",  True,  True),   # Noah - defective within 90 days (valid)
    ("ORD-015", 15, "Air Stride Pro",        10,  129.99,  0,  get_date(35), "delivered", "unworn",  True,  False),  # Olivia - Gold 45-day (valid)
]


def seed():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE customers (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            loyalty_tier TEXT DEFAULT 'Standard',
            annual_spend REAL DEFAULT 0.0
        )
    """)

    cur.execute("""
        CREATE TABLE orders (
            order_id TEXT PRIMARY KEY,
            customer_id INTEGER NOT NULL,
            product TEXT NOT NULL,
            size INTEGER,
            price REAL NOT NULL,
            discount_pct INTEGER DEFAULT 0,
            delivery_date TEXT NOT NULL,
            status TEXT DEFAULT 'delivered',
            condition TEXT DEFAULT 'unworn',
            has_receipt INTEGER DEFAULT 1,
            is_defective INTEGER DEFAULT 0,
            refund_status TEXT DEFAULT 'none',
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    cur.executemany("INSERT INTO customers VALUES (?,?,?,?,?,?)", CUSTOMERS)
    cur.executemany("INSERT INTO orders VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                    [(o[0], o[1], o[2], o[3], o[4], o[5], o[6], o[7], o[8],
                      int(o[9]), int(o[10]), "none") for o in ORDERS])

    conn.commit()
    conn.close()
    print(f"Database seeded at {DB_PATH}")
    print(f"  {len(CUSTOMERS)} customers | {len(ORDERS)} orders")


if __name__ == "__main__":
    seed()
