"""Billing context. Independent of orders by contract."""

from __future__ import annotations

from shop.shared.money import cents


def invoice_total(lines: list[tuple[int, float]]) -> int:
    return sum(cents(qty * price) for qty, price in lines)
