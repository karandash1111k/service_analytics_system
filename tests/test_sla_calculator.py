"""Unit tests for SLA analytics — deterministic scenarios."""

from datetime import datetime, timedelta, timezone

from analytics.sla_calculator import OrderSLAInput, SLACalculator


def test_sla_met_when_completed_within_target():
    calc = SLACalculator()
    created = datetime(2025, 1, 1, 8, 0, tzinfo=timezone.utc)
    completed = created + timedelta(hours=10)
    row = OrderSLAInput(
        order_id=1,
        priority="high",
        status="completed",
        created_at=created,
        completed_at=completed,
    )
    res = calc.evaluate_order(row, now=completed)
    assert res.breached is False


def test_sla_breach_when_overdue_open_ticket():
    calc = SLACalculator()
    created = datetime(2025, 1, 1, 8, 0, tzinfo=timezone.utc)
    row = OrderSLAInput(
        order_id=2,
        priority="high",
        status="in_progress",
        created_at=created,
        completed_at=None,
    )
    now = created + timedelta(hours=48)
    res = calc.evaluate_order(row, now=now)
    assert res.breached is True
