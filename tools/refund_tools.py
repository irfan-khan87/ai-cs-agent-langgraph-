import os
import sqlite3
from langchain_core.tools import tool

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sole_syntax.db")


@tool
def process_refund(order_id: str, reason: str) -> str:
    """
    Approve and process a refund for an eligible order.
    Only call this AFTER check_refund_eligibility confirms the order is ELIGIBLE.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT price, product, refund_status FROM orders WHERE UPPER(order_id) = UPPER(?)",
        (order_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return f"Error: Order '{order_id}' not found."

    price, product, refund_status = row
    if refund_status == "approved":
        conn.close()
        return f"Order {order_id} has already been refunded."

    cur.execute(
        "UPDATE orders SET refund_status = 'approved' WHERE UPPER(order_id) = UPPER(?)",
        (order_id,),
    )
    conn.commit()
    conn.close()

    return (
        f"REFUND APPROVED ✓\n"
        f"  Order: {order_id.upper()} — {product}\n"
        f"  Amount: ${price:.2f}\n"
        f"  Reason: {reason}\n"
        f"  The refund of ${price:.2f} will be returned to the original payment method "
        f"within 5–7 business days."
    )


@tool
def deny_refund(order_id: str, reason: str) -> str:
    """
    Deny a refund request for a non-eligible order.
    Only call this AFTER check_refund_eligibility confirms the order is DENIED.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT product, refund_status FROM orders WHERE UPPER(order_id) = UPPER(?)",
        (order_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return f"Error: Order '{order_id}' not found."

    product, refund_status = row
    if refund_status == "denied":
        conn.close()
        return f"Order {order_id} has already been denied."

    cur.execute(
        "UPDATE orders SET refund_status = 'denied' WHERE UPPER(order_id) = UPPER(?)",
        (order_id,),
    )
    conn.commit()
    conn.close()

    return (
        f"REFUND DENIED ✗\n"
        f"  Order: {order_id.upper()} — {product}\n"
        f"  Reason: {reason}\n"
        f"  If you believe this decision is incorrect, you may request escalation "
        f"to a human supervisor who will review your case within 24 hours."
    )


@tool
def escalate_to_human(order_id: str, issue_summary: str) -> str:
    """
    Escalate a disputed refund case to a human supervisor.
    Use when the customer disputes a denial or the case is too complex to resolve automatically.
    """
    return (
        f"ESCALATED TO SUPERVISOR ⚡\n"
        f"  Order: {order_id.upper()}\n"
        f"  Issue: {issue_summary}\n"
        f"  A Sole Syntax supervisor will review this case and contact the customer "
        f"via email within 24 hours. Reference this ticket for follow-up."
    )
