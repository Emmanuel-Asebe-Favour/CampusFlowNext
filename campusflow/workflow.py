from campusflow.validation import validate_staff_name


ALLOWED_STATUS_TRANSITIONS = {
    "open": {"in_progress"},
    "in_progress": {"resolved"},
    "resolved": set(),
}


def _find_ticket(tickets, ticket_id):
    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise ValueError(f"Unknown ticket ID: '{ticket_id}'.")


def _reject_if_resolved(ticket):
    if ticket["status"] == "resolved":
        raise ValueError(
            "Resolved tickets can only be modified after an explicit reopen."
        )

def assign_ticket(tickets, ticket_id, staff_name):
    staff_name = validate_staff_name(staff_name)

    ticket = _find_ticket(tickets, ticket_id)
    _reject_if_resolved(ticket)

    ticket["assigned_to"] = staff_name
    return ticket


def update_ticket_status(tickets, ticket_id, new_status):

    if not isinstance(new_status, str):
        raise ValueError("Status must be text.")
    
    ticket = _find_ticket(tickets, ticket_id)
    _reject_if_resolved(ticket)

    if new_status == "in_progress" and not ticket.get("assigned_to"):
        raise ValueError("Cannot move an unassigned ticket to in_progress.")

    current_status = ticket["status"]
    allowed = ALLOWED_STATUS_TRANSITIONS.get(current_status, set())

    if new_status not in allowed:
        raise ValueError(
            f"Invalid status transition from '{current_status}' to '{new_status}'."
        )

    ticket["status"] = new_status
    return ticket


def reopen_ticket(tickets, ticket_id):
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] != "resolved":
        raise ValueError("Only resolved tickets can be reopened.")

    ticket["status"] = "open"
    return ticket


def add_note(tickets, ticket_id, author, message):
    """Add a validated note to an open or in-progress ticket."""
    ticket = _find_ticket(tickets, ticket_id)

    if ticket["status"] not in {"open", "in_progress"}:
        raise ValueError(
            "A resolved ticket cannot accept notes until it is reopened."
        )

    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author must not be blank.")

    if not isinstance(message, str):
        raise ValueError(
            "Note message must be text between 5 and 300 characters."
        )

    message = message.strip()

    if not 5 <= len(message) <= 300:
        raise ValueError(
            "Note message must be between 5 and 300 characters."
        )

    notes = ticket.get("notes")

    if not isinstance(notes, list):
        raise ValueError("Ticket notes must be a list.")

    highest_id = 0
    seen_note_numbers = set()

    # Validate existing notes before adding anything.
    for existing_note in notes:
        if not isinstance(existing_note, dict):
            raise ValueError("Existing notes must be valid note objects.")

        required_fields = {"note_id", "author", "message"}
        if not required_fields.issubset(existing_note):
            raise ValueError(
                "Each note needs note_id, author, and message."
            )

        note_id = existing_note["note_id"]

        if (
            not isinstance(note_id, str)
            or not note_id.startswith("N")
            or not note_id[1:].isdigit()
        ):
            raise ValueError("Each existing note must have a valid note ID.")

        note_number = int(note_id[1:])

        if note_number < 1 or note_number in seen_note_numbers:
            raise ValueError("Existing note IDs must be unique and valid.")

        seen_note_numbers.add(note_number)
        highest_id = max(highest_id, note_number)

        existing_author = existing_note["author"]
        if (
            not isinstance(existing_author, str)
            or not existing_author.strip()
        ):
            raise ValueError("Existing note authors must not be blank.")

        existing_message = existing_note["message"]
        if (
            not isinstance(existing_message, str)
            or not 5 <= len(existing_message.strip()) <= 300
        ):
            raise ValueError(
                "Existing note messages must be between 5 and 300 characters."
            )

    # Create the new note only after all checks pass.
    note = {
        "note_id": f"N{highest_id + 1:03d}",
        "author": author.strip(),
        "message": message,
    }

    notes.append(note)
    ticket["notes"] = notes

    return note
