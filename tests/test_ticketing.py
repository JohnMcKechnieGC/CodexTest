import re
from datetime import datetime

import pytest

from ticketing import Priority, Status, TicketStore, format_timestamp


def test_create_ticket_assigns_incrementing_id_and_trims_fields():
    store = TicketStore()

    ticket = store.create_ticket(
        requester=" Alice ",
        contact=" alice@example.com ",
        subject=" Laptop issue ",
        description=" Won't start ",
        priority=Priority.HIGH,
    )

    assert ticket.id == 1
    assert ticket.requester == "Alice"
    assert ticket.contact == "alice@example.com"
    assert ticket.subject == "Laptop issue"
    assert ticket.description == "Won't start"

    next_ticket = store.create_ticket(
        requester="Bob",
        contact="bob@example.com",
        subject="Email problem",
        description="Cannot send",
        priority=Priority.MEDIUM,
    )

    assert next_ticket.id == 2


def test_resolve_ticket_updates_status_and_resolution_timestamp():
    store = TicketStore()
    ticket = store.create_ticket(
        requester="Alice",
        contact="alice@example.com",
        subject="Laptop issue",
        description="Won't start",
        priority=Priority.HIGH,
    )

    resolved = store.resolve_ticket(ticket.id, "Replaced the battery")

    assert resolved.status is Status.RESOLVED
    assert resolved.resolution == "Replaced the battery"
    assert isinstance(resolved.resolved_at, datetime)


@pytest.mark.parametrize(
    "ticket_id,resolution,expected_exception",
    [(999, "something", ValueError), (1, "   ", ValueError)],
)
def test_resolve_ticket_with_invalid_input_raises(ticket_id, resolution, expected_exception):
    store = TicketStore()
    store.create_ticket(
        requester="Alice",
        contact="alice@example.com",
        subject="Laptop issue",
        description="Won't start",
        priority=Priority.HIGH,
    )

    with pytest.raises(expected_exception):
        store.resolve_ticket(ticket_id, resolution)


def test_filtering_by_status_and_priority_returns_expected_subset():
    store = TicketStore()
    store.create_ticket(
        requester="Open Low",
        contact="open.low@example.com",
        subject="Issue",
        description="Desc",
        priority=Priority.LOW,
    )
    medium = store.create_ticket(
        requester="Open Medium",
        contact="open.medium@example.com",
        subject="Issue",
        description="Desc",
        priority=Priority.MEDIUM,
    )
    store.resolve_ticket(medium.id, "Solved")

    open_medium = store.filter_tickets(status=Status.OPEN, priority=Priority.MEDIUM)
    assert open_medium == []

    resolved_medium = store.filter_tickets(status=Status.RESOLVED, priority=Priority.MEDIUM)
    assert resolved_medium == [medium]


def test_stats_reports_total_open_resolved_counts():
    store = TicketStore()
    t1 = store.create_ticket(
        requester="A",
        contact="a@example.com",
        subject="Sub",
        description="Desc",
        priority=Priority.LOW,
    )
    store.create_ticket(
        requester="B",
        contact="b@example.com",
        subject="Sub",
        description="Desc",
        priority=Priority.LOW,
    )
    store.resolve_ticket(t1.id, "Done")

    total, open_count, resolved_count = store.stats()

    assert total == 2
    assert open_count == 1
    assert resolved_count == 1


def test_format_timestamp_returns_dash_for_none_and_expected_format():
    now = datetime(2024, 1, 1, 12, 0)
    assert format_timestamp(None) == "—"

    formatted = format_timestamp(now)

    assert re.match(r"^2024-01-01 12:00 UTC$", formatted)
