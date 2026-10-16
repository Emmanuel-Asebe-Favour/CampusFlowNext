
import json
import os
import tempfile

from campusflow.validation import validate_ticket

SCHEMA_VERSION = 1


def validate_collection(tickets):
    """Validate a complete ticket list and return clean copies."""
    if not isinstance(tickets, list):
        raise ValueError("Tickets must be provided as a list.")

    validated = []
    seen_ids = set()

    for index, ticket in enumerate(tickets, start=1):
        if not isinstance(ticket, dict):
            raise ValueError(
                f"Record {index}: each ticket must be a dictionary."
            )

        try:
            clean_ticket = validate_ticket(ticket)
        except ValueError as error:
            message = str(error)
            lowered_message = message.lower()

            if "priority" in lowered_message:
                message = f"Priority validation failed: {message}"
            elif "category" in lowered_message:
                message = f"Invalid category: {message}"

            raise ValueError(
                f"Record {index}: {message}"
            ) from error

        ticket_id = clean_ticket["id"]

        if ticket_id in seen_ids:
            raise ValueError(
                f"Duplicate ticket ID (duplicate ticket ID): '{ticket_id}'."
            )

        seen_ids.add(ticket_id)
        validated.append(clean_ticket)

    return validated


def save_tickets(tickets, path):
    """Validate tickets and safely save them to a JSON file."""
    # Validate before touching the existing file.
    validated = validate_collection(tickets)

    data = {
        "schema_version": SCHEMA_VERSION,
        "tickets": validated,
    }

    directory = os.path.dirname(path) or "."
    os.makedirs(directory, exist_ok=True)

    # Write to a temporary file, then replace the destination.
    fd, temp_path = tempfile.mkstemp(
        dir=directory,
        suffix=".tmp",
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        os.replace(temp_path, path)

    except BaseException:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def load_tickets(path):
    """Load tickets from JSON and validate the complete collection."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError(
                f"Cannot load tickets from '{path}': "
                "expected a JSON object."
            )

        version = data.get("schema_version")

        # Reject True, even though True == 1 in Python.
        if type(version) is not int or version != SCHEMA_VERSION:
            raise ValueError(
                f"Cannot load tickets from '{path}': "
                "unsupported or missing schema version."
            )

        try:
            return validate_collection(data.get("tickets"))
        except ValueError as error:
            raise ValueError(
                f"Cannot load tickets from '{path}': {error}"
            ) from error

    except FileNotFoundError:
        # A missing file means the application can start fresh.
        return []

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Cannot load tickets from '{path}': "
            f"invalid JSON at line {error.lineno}, "
            f"column {error.colno}."
        ) from error


def reload_into(tickets, path):
    """Replace in-memory tickets only after loading succeeds."""
    loaded = load_tickets(path)
    tickets[:] = loaded
    return tickets


def generate_ticket_id(tickets):
    """Generate the next ticket ID using the highest existing number."""
    highest_id = 0

    for ticket in tickets:
        if not isinstance(ticket, dict):
            continue

        ticket_id = ticket.get("id")

        if (
            isinstance(ticket_id, str)
            and ticket_id.startswith("T")
            and ticket_id[1:].isascii()
            and ticket_id[1:].isdigit()
        ):
            highest_id = max(
                highest_id,
                int(ticket_id[1:]),
            )

    return f"T{highest_id + 1:03d}"
