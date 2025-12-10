"""
Streamlit demo app for an in-memory IT helpdesk ticketing system.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

import streamlit as st


@dataclass
class Ticket:
    """Simple ticket model stored in Streamlit session state."""

    id: int
    requester: str
    contact: str
    subject: str
    description: str
    priority: str
    status: str = "Open"
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolution: Optional[str] = None
    resolved_at: Optional[datetime] = None

    def resolve(self, resolution: str) -> None:
        """Resolve a ticket with the provided resolution notes."""
        self.status = "Resolved"
        self.resolution = resolution
        self.resolved_at = datetime.utcnow()


def init_state() -> None:
    """Initialize the session state container for tickets."""
    if "tickets" not in st.session_state:
        st.session_state.tickets: List[Ticket] = []


def add_ticket(ticket: Ticket) -> None:
    """Persist a ticket to session state."""
    st.session_state.tickets.append(ticket)


def get_next_ticket_id() -> int:
    """Return the next sequential ticket identifier."""
    if not st.session_state.tickets:
        return 1
    return max(ticket.id for ticket in st.session_state.tickets) + 1


def resolve_ticket(ticket_id: int, resolution: str) -> None:
    """Resolve the ticket matching the given identifier."""
    for ticket in st.session_state.tickets:
        if ticket.id == ticket_id:
            ticket.resolve(resolution)
            break


def format_timestamp(timestamp: Optional[datetime]) -> str:
    """Return a human-friendly timestamp string for display."""
    if timestamp is None:
        return "—"
    return timestamp.strftime("%Y-%m-%d %H:%M UTC")


def render_ticket(ticket: Ticket) -> None:
    """Render a single ticket and its resolution form if open."""
    with st.expander(f"[#{ticket.id}] {ticket.subject} — {ticket.status}"):
        st.markdown(
            f"**Requester:** {ticket.requester}\n\n"
            f"**Contact:** {ticket.contact}\n\n"
            f"**Priority:** {ticket.priority}\n\n"
            f"**Created:** {format_timestamp(ticket.created_at)}"
        )
        st.markdown("**Issue description**")
        st.write(ticket.description)

        if ticket.status == "Open":
            st.divider()
            st.markdown("**Add resolution**")
            resolution_text = st.text_area(
                "Resolution notes",
                placeholder="Document what resolved the issue",
                key=f"resolution_{ticket.id}",
            )
            resolve_col1, resolve_col2 = st.columns([1, 3])
            with resolve_col1:
                if st.button(
                    "Resolve ticket",
                    key=f"resolve_btn_{ticket.id}",
                    type="primary",
                    disabled=not resolution_text.strip(),
                ):
                    resolve_ticket(ticket.id, resolution_text.strip())
                    st.success("Ticket marked as resolved.")
                    st.experimental_rerun()
        else:
            st.success("Resolved")
            st.markdown(f"**Resolution:** {ticket.resolution}")
            st.markdown(f"**Resolved:** {format_timestamp(ticket.resolved_at)}")


def render_ticket_board(tickets: List[Ticket]) -> None:
    """Render a list of tickets with optional filtering."""
    st.subheader("Ticket board")
    st.caption(
        "Tickets are stored in memory for this demo and reset whenever the app restarts."
    )

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        status_filter = st.selectbox(
            "Status", ["All", "Open", "Resolved"], index=0, key="status_filter"
        )
    with filter_col2:
        priority_filter = st.selectbox(
            "Priority", ["All", "Low", "Medium", "High"], index=0, key="priority_filter"
        )

    filtered_tickets = [
        ticket
        for ticket in tickets
        if (status_filter == "All" or ticket.status == status_filter)
        and (priority_filter == "All" or ticket.priority == priority_filter)
    ]

    if not filtered_tickets:
        st.info("No tickets match the selected filters.")
        return

    for ticket in sorted(filtered_tickets, key=lambda t: t.created_at, reverse=True):
        render_ticket(ticket)


def render_new_ticket_form() -> None:
    """Render the form for logging a new ticket."""
    st.subheader("Log a new ticket")
    with st.form("new_ticket"):
        requester = st.text_input("Requester name")
        contact = st.text_input("Contact (email or phone)")
        subject = st.text_input("Subject")
        description = st.text_area("Issue description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)

        submitted = st.form_submit_button("Submit ticket", type="primary")
        if submitted:
            if not all([requester.strip(), contact.strip(), subject.strip(), description.strip()]):
                st.error("Please complete all required fields before submitting.")
            else:
                ticket = Ticket(
                    id=get_next_ticket_id(),
                    requester=requester.strip(),
                    contact=contact.strip(),
                    subject=subject.strip(),
                    description=description.strip(),
                    priority=priority,
                )
                add_ticket(ticket)
                st.success(f"Ticket #{ticket.id} has been logged.")
                st.experimental_rerun()


def main() -> None:
    st.set_page_config(page_title="In-memory Helpdesk", page_icon="🛠️", layout="wide")
    st.title("IT Helpdesk Demo")
    st.caption("Log and resolve tickets in-memory. Data resets when the app restarts.")

    init_state()

    stats_col1, stats_col2, stats_col3 = st.columns(3)
    total_tickets = len(st.session_state.tickets)
    open_tickets = len([t for t in st.session_state.tickets if t.status == "Open"])
    resolved_tickets = total_tickets - open_tickets

    stats_col1.metric("Total tickets", total_tickets)
    stats_col2.metric("Open", open_tickets)
    stats_col3.metric("Resolved", resolved_tickets)

    form_col, board_col = st.columns([2, 3], gap="large")
    with form_col:
        render_new_ticket_form()

    with board_col:
        render_ticket_board(st.session_state.tickets)


if __name__ == "__main__":
    main()
