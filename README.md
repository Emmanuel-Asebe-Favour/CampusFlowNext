# CampusFlow Helpdesk

CampusFlow is a Python command-line helpdesk application for creating, tracking, assigning, and resolving IT support tickets.

## Features

- Create and manage support tickets.
- Validate ticket titles, categories, urgency, and affected users.
- Calculate ticket priority automatically.
- List tickets and look up ticket details.
- Assign tickets to staff members.
- Manage ticket status transitions and reopen resolved tickets.
- Add notes to open and in-progress tickets.
- Display an unresolved-work queue ordered by priority and ticket ID.
- Generate reports grouped by status and priority.
- Save tickets to JSON and reload them when the application starts.
- Reject invalid operations safely without changing ticket data.
- Run automated tests using Python's standard library.

## Ticket Validation and Workflow Safety

CampusFlow validates ticket data before accepting changes.

- Ticket titles must not be blank.
- Categories must be `Network`, `Hardware`, `Software`, or `Other`.
- Urgency must be `low`, `medium`, or `high`.
- The number of affected users must be a positive integer.
- Ticket IDs must be valid and unique.
- Assigned staff names must not be blank.
- An unassigned ticket cannot move to `in_progress`.
- Tickets follow the permitted status transitions: `open` → `in_progress` → `resolved`.
- A resolved ticket must be explicitly reopened before it can be reassigned or receive new notes.

Rejected operations should leave the affected ticket data unchanged.

## Ticket Notes

Each note contains:

- `note_id`: a sequential ID such as `N001`.
- `author`: the staff member who added the note.
- `message`: the note content.

Note IDs must be unique within each ticket. Authors must not be blank, and messages must contain between 5 and 300 characters after trimming surrounding whitespace.

Notes can be added only to open or in-progress tickets. Existing notes are preserved when a ticket is resolved and later reopened.

## JSON Storage

Tickets are stored in JSON using a versioned structure:

```json
{
  "schema_version": 1,
  "tickets": []
}
```

The `tickets` list contains the saved ticket records.

Storage validation checks required ticket fields, unique ticket IDs, valid categories and urgency values, legal statuses, priority consistency, assignment values, and note structure.

- A missing storage file returns an empty ticket list.
- Malformed JSON produces a clear error.
- Invalid ticket data is rejected instead of being silently accepted.
- Ticket data is validated before it is saved.
- Ticket IDs are generated using the highest existing numeric ID to avoid collisions after reloading saved tickets.

## Requirements

- Python 3.10 or later.
- Python standard library only; no external packages are required.

## Run the Application

From the project root, run:

```bash
python3 -m campusflow.main
```

Follow the numbered menu to use the application. Ticket data is stored locally in `data/tickets.json`.

## Run the Tests

Run the complete test suite from the project root:

```bash
python3 -m unittest discover -s tests -v
```

The tests cover ticket creation, validation, priority calculation, assignment, workflow rules, reopening, notes, JSON persistence, ticket ID generation, queue ordering, and reporting.

## Project Structure

```text
campusflow/
    main.py
    tickets.py
    workflow.py
    queue.py
    reports.py
    storage.py
tests/
    test_tickets.py
    test_workflow.py
    test_storage.py
    test_queue_reports.py
data/
README.md
```

## Team Development

CampusFlow is developed collaboratively. Changes are made on feature branches, tested before submission, and submitted through pull requests for review before being merged into the main branch.

The `data/` directory is excluded from Git so local runtime data is not accidentally committed.
