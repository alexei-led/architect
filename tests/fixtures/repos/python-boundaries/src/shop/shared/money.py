"""Shared, dependency-free helpers both contexts may use."""

from __future__ import annotations


def cents(amount: float) -> int:
    return round(amount * 100)
