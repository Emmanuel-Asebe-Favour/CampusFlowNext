
import unittest
import copy

from campusflow.workflow import (
    add_note,
    assign_ticket,
    reopen_ticket,
    update_ticket_status,
)


def _make_ticket(ticket_id, status="open", assigned_to=None):
    return {
        "id": ticket_id, "title": "Sample", "category": "Network",
        "urgency": "low", "affected_users": 1, "priority": "low",
        "status": status, "assigned_to": assigned_to,
    }


class TestStatusSafety(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            _make_ticket("T001"),                                
            _make_ticket("T002", "resolved", assigned_to="Sam"),   
        ]
        self.before = copy.deepcopy(self.tickets)

    def test_unassigned_open_to_in_progress_rejected_and_unchanged(self):
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T001", "in_progress")
        self.assertEqual(self.tickets, self.before)

    def test_assign_resolved_ticket_rejected_and_unchanged(self):
        with self.assertRaises(ValueError):
            assign_ticket(self.tickets, "T002", "Alex")
        self.assertEqual(self.tickets, self.before)

    def test_reopen_open_ticket_rejected_and_unchanged(self):
        with self.assertRaises(ValueError):
            reopen_ticket(self.tickets, "T001")
        self.assertEqual(self.tickets, self.before)

    def test_unknown_ticket_id_leaves_collection_unchanged(self):
        with self.assertRaises(ValueError):
            update_ticket_status(self.tickets, "T999", "in_progress")
        self.assertEqual(self.tickets, self.before)

    def test_non_string_status_rejected_with_value_error(self):
        for bad in (["in_progress"], {"a": 1}, None, 5):
            with self.subTest(status=bad):
                with self.assertRaises(ValueError):
                    update_ticket_status(self.tickets, "T001", bad)
                self.assertEqual(self.tickets, self.before)


class TestAssignTicket(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Network connection is down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            }
        ]

    def test_assign_sets_staff_name(self):
        ticket = assign_ticket(self.tickets, "T001", "Ada")

        self.assertIs(ticket, self.tickets[0])
        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_assign_trims_staff_name(self):
        ticket = assign_ticket(self.tickets, "T001", "  Ada  ")

        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_assign_rejects_unknown_ticket_id(self):
        with self.assertRaisesRegex(ValueError, "Unknown ticket ID"):
            assign_ticket(self.tickets, "T999", "Ada")

        self.assertIsNone(self.tickets[0]["assigned_to"])

    def test_assign_rejects_blank_staff_name(self):
        with self.assertRaisesRegex(ValueError, "Staff name must not be blank"):
            assign_ticket(self.tickets, "T001", "   ")

        self.assertIsNone(self.tickets[0]["assigned_to"])


class TestTicketWorkflow(unittest.TestCase):

    def setUp(self):
        self.tickets = [
            {
                "id": "T001",
                "title": "Network connection is down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
                "notes": [],
            }
        ]

    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        with self.assertRaisesRegex(ValueError, "unassigned"):
            update_ticket_status(self.tickets, "T001", "in_progress")

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_assigned_ticket_progresses_open_in_progress_resolved(self):
        assign_ticket(self.tickets, "T001", "Ada")

        in_progress = update_ticket_status(self.tickets, "T001", "in_progress")
        self.assertEqual(in_progress["status"], "in_progress")

        resolved = update_ticket_status(self.tickets, "T001", "resolved")
        self.assertEqual(resolved["status"], "resolved")
        self.assertIs(resolved, self.tickets[0])

    def test_rejects_skipping_from_open_to_resolved(self):
        assign_ticket(self.tickets, "T001", "Ada")

        with self.assertRaisesRegex(ValueError, "Invalid status transition"):
            update_ticket_status(self.tickets, "T001", "resolved")

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_resolved_ticket_cannot_change_status_without_reopen(self):
        assign_ticket(self.tickets, "T001", "Ada")
        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")

        with self.assertRaisesRegex(ValueError, "explicit reopen"):
            update_ticket_status(self.tickets, "T001", "in_progress")

        self.assertEqual(self.tickets[0]["status"], "resolved")

    def test_reopen_sets_resolved_ticket_to_open(self):
        assign_ticket(self.tickets, "T001", "Ada")
        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")

        ticket = reopen_ticket(self.tickets, "T001")

        self.assertEqual(ticket["status"], "open")
        self.assertEqual(ticket["assigned_to"], "Ada")

    def test_reopen_rejects_ticket_that_is_not_resolved(self):
        with self.assertRaisesRegex(ValueError, "Only resolved tickets"):
            reopen_ticket(self.tickets, "T001")

        self.assertEqual(self.tickets[0]["status"], "open")

    def test_assign_rejects_resolved_ticket_until_reopen(self):
        assign_ticket(self.tickets, "T001", "Ada")
        update_ticket_status(self.tickets, "T001", "in_progress")
        update_ticket_status(self.tickets, "T001", "resolved")

        with self.assertRaisesRegex(ValueError, "explicit reopen"):
            assign_ticket(self.tickets, "T001", "Ben")

        self.assertEqual(self.tickets[0]["assigned_to"], "Ada")

    def test_update_status_rejects_unknown_ticket_id(self):
        with self.assertRaisesRegex(ValueError, "Unknown ticket ID"):
            update_ticket_status(self.tickets, "T999", "in_progress")


class TestAddNote(unittest.TestCase):

    def setUp(self):
        self.tickets = [{
            "id": "T001",
            "title": "Network connection is down",
            "category": "Network",
            "urgency": "high",
            "affected_users": 12,
            "priority": "critical",
            "status": "open",
            "assigned_to": None,
            "notes": [],
        }]

    def test_add_note_creates_note_with_id(self):
        note = add_note(
            self.tickets, "T001", "Ada", "Network is being checked."
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(note["author"], "Ada")
        self.assertEqual(note["message"], "Network is being checked.")
        self.assertEqual(len(self.tickets[0]["notes"]), 1)

    def test_add_note_rejects_blank_author(self):
        with self.assertRaisesRegex(ValueError, "author"):
            add_note(self.tickets, "T001", "   ", "A valid note.")

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_add_note_rejects_short_message(self):
        with self.assertRaisesRegex(ValueError, "5"):
            add_note(self.tickets, "T001", "Ada", "Hey")

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_add_note_rejects_resolved_ticket(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaisesRegex(ValueError, "resolved"):
            add_note(
                self.tickets,
                "T001",
                "Ada",
                "This note should be rejected.",
            )

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_rejected_note_does_not_consume_id(self):
        with self.assertRaises(ValueError):
            add_note(self.tickets, "T001", " ", "Invalid author.")

        note = add_note(
            self.tickets, "T001", "Ada", "This note should be accepted."
        )

        self.assertEqual(note["note_id"], "N001")

    def test_add_note_rejects_long_message(self):
        with self.assertRaisesRegex(ValueError, "300"):
            add_note(self.tickets, "T001", "Ada", "x" * 301)

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_add_note_rejects_unknown_ticket(self):
        with self.assertRaisesRegex(ValueError, "Unknown ticket ID"):
            add_note(
                self.tickets,
                "T999",
                "Ada",
                "This ticket does not exist.",
            )

        self.assertEqual(self.tickets[0]["notes"], [])

    def test_add_note_rejects_malformed_existing_note(self):
        self.tickets[0]["notes"] = [
            {"note_id": "N001", "author": "Ada"}
        ]
        original_notes = [
            note.copy() for note in self.tickets[0]["notes"]
        ]

        with self.assertRaisesRegex(ValueError, "message"):
            add_note(
                self.tickets,
                "T001",
                "Ada",
                "This new note should be rejected.",
            )

        self.assertEqual(self.tickets[0]["notes"], original_notes)

    def test_add_note_rejects_duplicate_numeric_note_ids(self):
        self.tickets[0]["notes"] = [
            {
                "note_id": "N001",
                "author": "Ada",
                "message": "First existing note.",
            },
            {
                "note_id": "N1",
                "author": "Joy",
                "message": "Second existing note.",
            },
        ]
        original_notes = [
            note.copy() for note in self.tickets[0]["notes"]
        ]

        with self.assertRaisesRegex(ValueError, "unique"):
            add_note(
                self.tickets,
                "T001",
                "Ada",
                "This new note should be rejected.",
            )

        self.assertEqual(self.tickets[0]["notes"], original_notes)

    def test_add_note_after_reopening_resolved_ticket(self):
        self.tickets[0]["status"] = "resolved"

        with self.assertRaisesRegex(ValueError, "resolved"):
            add_note(
                self.tickets,
                "T001",
                "Ada",
                "This ticket is still resolved.",
            )

        reopen_ticket(self.tickets, "T001")

        note = add_note(
            self.tickets,
            "T001",
            "Ada",
            "The ticket has been reopened.",
        )

        self.assertEqual(note["note_id"], "N001")
        self.assertEqual(self.tickets[0]["status"], "open")


if __name__ == "__main__":
    unittest.main()
