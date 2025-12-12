"""
Domain logic for in-memory helpdesk tickets.

This module is streamlit-agnostic to enable straightforward unit testing.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional, Sequence


class Status(str, Enum):
    OPEN = "Open"
    RESOLVED = "Resolved"


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


@dataclass
class Ticket:
    """Simple ticket model."""

    id: int
    requester: str
    contact: str
    subject: str
    description: str
    priority: Priority
    status: Status = Status.OPEN
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

    def resolve(self, resolution: str) -> None:
        """Resolve a ticket with the provided resolution notes."""
        if not resolution.strip():
            raise ValueError("Resolution cannot be empty")
        self.status = Status.RESOLVED
        self.resolution = resolution.strip()
        self.resolved_at = datetime.utcnow()


class TicketStore:
    """In-memory store for tickets with predictable ID assignment."""

    def __init__(self, tickets: Optional[Sequence[Ticket]] = None) -> None:
        self._tickets: List[Ticket] = list(tickets) if tickets else []
        self._next_id: int = self._compute_next_id()

    def _compute_next_id(self) -> int:
        if not self._tickets:
            return 1
        return max(ticket.id for ticket in self._tickets) + 1

    @property
    def tickets(self) -> List[Ticket]:
        return list(self._tickets)

    def create_ticket(
        self, requester: str, contact: str, subject: str, description: str, priority: Priority
    ) -> Ticket:
        ticket = Ticket(
            id=self._next_id,
            requester=requester.strip(),
            contact=contact.strip(),
            subject=subject.strip(),
            description=description.strip(),
            priority=priority,
        )
        self._tickets.append(ticket)
        self._next_id += 1
        return ticket

    def resolve_ticket(self, ticket_id: int, resolution: str) -> Ticket:
        ticket = self.get_ticket(ticket_id)
        if ticket is None:
            raise ValueError(f"Ticket {ticket_id} not found")
        ticket.resolve(resolution)
        return ticket

    def get_ticket(self, ticket_id: int) -> Optional[Ticket]:
        return next((t for t in self._tickets if t.id == ticket_id), None)

    def filter_tickets(
        self, status: Optional[Status] = None, priority: Optional[Priority] = None
    ) -> List[Ticket]:
        return [
            t
            for t in self._tickets
            if (status is None or t.status == status)
            and (priority is None or t.priority == priority)
        ]

    def stats(self) -> tuple[int, int, int]:
        total = len(self._tickets)
        open_count = len([t for t in self._tickets if t.status == Status.OPEN])
        resolved_count = total - open_count
        return total, open_count, resolved_count


def format_timestamp(timestamp: Optional[datetime]) -> str:
    """Return a human-friendly timestamp string for display."""
    if timestamp is None:
        return "—"
    return timestamp.strftime("%Y-%m-%d %H:%M UTC")
