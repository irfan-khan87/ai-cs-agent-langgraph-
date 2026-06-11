import os
import sqlite3
from datetime import date
from langchain_core.tools import tool

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sole_syntax.db")

RETURN_WINDOWS = {"Standard": 30, "Gold": 45, "Platinum": 60}


@tool
def check_refund_eligibility(order_id: str) -> str:
    """
    Validate whether an order is eligible for a refund based on Sole Syntax policy.
    Returns a detailed eligibility verdict with the specific rule that applies.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """SELECT o.order_id, c.loyalty_tier, o.product, o.price,
                  o.discount_pct, o.delivery_date, o.condition,
                  o.has_receipt, o.is_defective, o.refund_status
           FROM orders o JOIN customers c ON o.customer_id = c.id
           WHERE UPPER(o.order_id) = UPPER(?)""",
        (order_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return f"Cannot check eligibility: order '{order_id}' not found."

    (oid, tier, product, price, discount, delivery_date_str,
     condition, has_receipt, is_defective, refund_status) = row

    if refund_status == "approved":
        return f"DENIED: Order {oid} has already been refunded."
    if refund_status == "denied":
        return f"DENIED: Order {oid} was previously denied. Customer may escalate to a supervisor."

    days_since_delivery = (date.today() - date.fromisoformat(delivery_date_str)).days
    return_window = RETURN_WINDOWS.get(tier, 30)

    # Rule 1: No receipt
    if not has_receipt:
        return (
            f"DENIED — Policy Rule 3: No valid Order ID or receipt on file for {oid}. "
            f"Returns cannot be processed without proof of purchase."
        )

    # Rule 2: Final sale (discount >= 20%)
    if discount >= 20:
        return (
            f"DENIED — Policy Rule 4: '{product}' was purchased at {discount}% discount "
            f"(≥20%), making it a Final Sale item. Final Sale items are non-returnable."
        )

    # Rule 3: Customized item
    if "custom" in product.lower():
        return (
            f"DENIED — Policy Rule 9: '{product}' is a customized/personalized item. "
            f"Custom orders are non-returnable."
        )

    # Rule 4: Defective item (90-day window)
    if is_defective:
        if days_since_delivery <= 90:
            return (
                f"ELIGIBLE — Policy Rule 5: '{product}' has a reported manufacturing defect. "
                f"Delivered {days_since_delivery} days ago (within the 90-day defect window). "
                f"Approved for full refund or replacement."
            )
        else:
            return (
                f"DENIED — Policy Rule 5: Defect reported {days_since_delivery} days after delivery "
                f"(90-day defect window expired)."
            )

    # Rule 5: Return window
    if days_since_delivery > return_window:
        return (
            f"DENIED — Policy Rule 1 & 6: Order delivered {days_since_delivery} days ago. "
            f"{tier} tier return window is {return_window} days. Return window has expired."
        )

    # Rule 6: Item condition
    if condition != "unworn":
        return (
            f"DENIED — Policy Rule 2: '{product}' shows signs of wear (condition: {condition}). "
            f"Only unworn items in original condition are eligible for return."
        )

    return (
        f"ELIGIBLE — '{product}' (Order {oid}) meets all return criteria:\n"
        f"  ✓ Delivered {days_since_delivery} days ago (within {return_window}-day window for {tier} tier)\n"
        f"  ✓ Item condition: {condition}\n"
        f"  ✓ Proof of purchase on file\n"
        f"  ✓ Not a final sale item\n"
        f"Approved for full refund of ${price:.2f}."
    )
