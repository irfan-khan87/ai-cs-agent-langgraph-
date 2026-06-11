import os
import sqlite3
from langchain_core.tools import tool

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sole_syntax.db")


def _get_conn():
    return sqlite3.connect(DB_PATH)


@tool
def lookup_customer(query: str) -> str:
    """Look up a customer by email address or full name. Returns customer profile and loyalty tier."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, name, email, phone, loyalty_tier, annual_spend FROM customers "
        "WHERE LOWER(email) = LOWER(?) OR LOWER(name) = LOWER(?)",
        (query, query),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return f"No customer found matching '{query}'. Please verify the email or name."
    cid, name, email, phone, tier, spend = row
    return (
        f"Customer found:\n"
        f"  ID: {cid}\n"
        f"  Name: {name}\n"
        f"  Email: {email}\n"
        f"  Phone: {phone}\n"
        f"  Loyalty Tier: {tier}\n"
        f"  Annual Spend: ${spend:.2f}"
    )


@tool
def get_order_details(order_id: str) -> str:
    """Retrieve full order details by Order ID (e.g. ORD-001)."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """SELECT o.order_id, c.name, c.email, c.loyalty_tier,
                  o.product, o.size, o.price, o.discount_pct,
                  o.delivery_date, o.status, o.condition,
                  o.has_receipt, o.is_defective, o.refund_status
           FROM orders o JOIN customers c ON o.customer_id = c.id
           WHERE UPPER(o.order_id) = UPPER(?)""",
        (order_id,),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        return f"No order found with ID '{order_id}'."
    (oid, name, email, tier, product, size, price, discount,
     delivery, status, condition, has_receipt, is_defective, refund_status) = row
    return (
        f"Order Details:\n"
        f"  Order ID: {oid}\n"
        f"  Customer: {name} ({email}) — {tier} tier\n"
        f"  Product: {product} | Size: {size}\n"
        f"  Price: ${price:.2f} | Discount: {discount}%\n"
        f"  Delivery Date: {delivery}\n"
        f"  Order Status: {status}\n"
        f"  Item Condition: {condition}\n"
        f"  Has Receipt/Order ID: {'Yes' if has_receipt else 'No'}\n"
        f"  Defective: {'Yes' if is_defective else 'No'}\n"
        f"  Current Refund Status: {refund_status}"
    )
