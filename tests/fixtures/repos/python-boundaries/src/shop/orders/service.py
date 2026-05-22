"""Orders context.

Contract violation: orders must not depend on billing, but this module imports
``shop.billing.invoice`` directly. import-linter flags the broken independence
contract.
"""

from __future__ import annotations

from shop.billing.invoice import invoice_total
from shop.shared.money import cents


def place_order(lines: list[tuple[int, float]]) -> int:
    subtotal = sum(cents(qty * price) for qty, price in lines)
    # Crossing the boundary instead of going through a shared abstraction.
    return max(subtotal, invoice_total(lines))
