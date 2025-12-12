"""
Streamlit demo app for an in-memory IT helpdesk ticketing system.
"""
from __future__ import annotations

from typing import Optional

import streamlit as st

from ticketing import Priority, Status, Ticket, TicketStore, format_timestamp


PRIORITY_OPTIONS = [Priority.LOW.value, Priority.MEDIUM.value, Priority.HIGH.value]
STATUS_OPTIONS = [Status.OPEN.value, Status.RESOLVED.value]


def get_ticket_store() -> TicketStore:
    """Retrieve or initialize the ticket store in session state."""
    if "ticket_store" not in st.session_state:
        st.session_state.ticket_store = TicketStore()
    return st.session_state.ticket_store


def render_ticket(ticket: Ticket, store: TicketStore) -> None:
    """Render a single ticket and its resolution form if open."""
    with st.expander(f"[#{ticket.id}] {ticket.subject} — {ticket.status.value}"):
        st.markdown(
            f"**Requester:** {ticket.requester}\n\n"
            f"**Contact:** {ticket.contact}\n\n"
            f"**Priority:** {ticket.priority.value}\n\n"
            f"**Created:** {format_timestamp(ticket.created_at)}"
        )
        st.markdown("**Issue description**")
        st.write(ticket.description)

        if ticket.status == Status.OPEN:
            st.divider()
            st.markdown("**Add resolution**")
            resolution_text = st.text_area(
                "Resolution notes",
                placeholder="Document what resolved the issue",
                key=f"resolution_{ticket.id}",
            )
            resolve_col1, _ = st.columns([1, 3])
            with resolve_col1:
                if st.button(
                    "Resolve ticket",
                    key=f"resolve_btn_{ticket.id}",
                    type="primary",
                    disabled=not resolution_text.strip(),
                ):
                    store.resolve_ticket(ticket.id, resolution_text)
                    st.success("Ticket marked as resolved.")
                    st.rerun()
        else:
            st.success("Resolved")
            st.markdown(f"**Resolution:** {ticket.resolution}")
            st.markdown(f"**Resolved:** {format_timestamp(ticket.resolved_at)}")


def _parse_status_filter(selection: str) -> Optional[Status]:
    if selection == "All":
        return None
    return Status(selection)


def _parse_priority_filter(selection: str) -> Optional[Priority]:
    if selection == "All":
        return None
    return Priority(selection)


def render_ticket_board(store: TicketStore) -> None:
    """Render a list of tickets with optional filtering."""
    st.subheader("Ticket board")
    st.caption(
        "Tickets are stored in memory for this demo and reset whenever the app restarts."
    )

    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        status_filter = st.selectbox(
            "Status", ["All", *STATUS_OPTIONS], index=0, key="status_filter"
        )
    with filter_col2:
        priority_filter = st.selectbox(
            "Priority", ["All", *PRIORITY_OPTIONS], index=0, key="priority_filter"
        )

    filtered_tickets = store.filter_tickets(
        status=_parse_status_filter(status_filter),
        priority=_parse_priority_filter(priority_filter),
    )

    if not filtered_tickets:
        st.info("No tickets match the selected filters.")
        return

    for ticket in sorted(filtered_tickets, key=lambda t: t.created_at, reverse=True):
        render_ticket(ticket, store)


def render_new_ticket_form(store: TicketStore) -> None:
    """Render the form for logging a new ticket."""
    st.subheader("Log a new ticket")
    with st.form("new_ticket"):
        requester = st.text_input("Requester name")
        contact = st.text_input("Contact (email or phone)")
        subject = st.text_input("Subject")
        description = st.text_area("Issue description")
        priority = st.selectbox("Priority", PRIORITY_OPTIONS, index=1)

        submitted = st.form_submit_button("Submit ticket", type="primary")
        if submitted:
            missing_fields = [
                label
                for label, value in {
                    "Requester name": requester,
                    "Contact": contact,
                    "Subject": subject,
                    "Issue description": description,
                }.items()
                if not value.strip()
            ]
            if missing_fields:
                st.error("Please complete all required fields before submitting.")
            else:
                ticket = store.create_ticket(
                    requester=requester,
                    contact=contact,
                    subject=subject,
                    description=description,
                    priority=Priority(priority),
                )
                st.success(f"Ticket #{ticket.id} has been logged.")
                st.rerun()


def main() -> None:
    st.set_page_config(page_title="In-memory Helpdesk", page_icon="🛠️", layout="wide")
    st.title("IT Helpdesk Demo")
    st.caption("Log and resolve tickets in-memory. Data resets when the app restarts.")

    store = get_ticket_store()

    stats_col1, stats_col2, stats_col3 = st.columns(3)
    total_tickets, open_tickets, resolved_tickets = store.stats()

    stats_col1.metric("Total tickets", total_tickets)
    stats_col2.metric("Open", open_tickets)
    stats_col3.metric("Resolved", resolved_tickets)

    form_col, board_col = st.columns([2, 3], gap="large")
    with form_col:
        render_new_ticket_form(store)

    with board_col:
        render_ticket_board(store)


if __name__ == "__main__":
    main()
