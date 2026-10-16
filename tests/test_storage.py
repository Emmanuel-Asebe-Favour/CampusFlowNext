
import copy
import json
import os
import tempfile
import unittest

from campusflow.notes import next_note_id
from campusflow.storage import (
    save_tickets,
    load_tickets,
    generate_ticket_id,
    reload_into,
)


class TestStorage(unittest.TestCase):

    def setUp(self):
        os.makedirs("data", exist_ok=True)
        self.path = "data/test_unittest_tickets.json"

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

    def tearDown(self):
        if os.path.exists(self.path):
            os.remove(self.path)

    def test_save_and_load_tickets(self):
        save_tickets(self.tickets, self.path)
        loaded_tickets = load_tickets(self.path)
        self.assertEqual(loaded_tickets, self.tickets)

    def test_load_rejects_duplicate_ticket_ids(self):
        ticket_one = self.tickets[0].copy()
        ticket_two = self.tickets[0].copy()

        ticket_one["id"] = "T001"
        ticket_two["id"] = "T001"

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "schema_version": 1,
                    "tickets": [ticket_one, ticket_two],
                },
                file,
            )

        with self.assertRaisesRegex(ValueError, "Duplicate ticket ID"):
            load_tickets(self.path)

    def test_load_rejects_invalid_ticket_id(self):
        invalid_ticket = {**self.tickets[0], "id": "BAD-ID"}

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "valid ticket ID"):
            load_tickets(self.path)

    def test_load_rejects_invalid_urgency(self):
        invalid_ticket = self.tickets[0].copy()
        invalid_ticket["urgency"] = "extreme"

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "urgency"):
            load_tickets(self.path)

    def test_load_rejects_incorrect_priority(self):
        invalid_ticket = self.tickets[0].copy()
        invalid_ticket["priority"] = "low"

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "Priority"):
            load_tickets(self.path)

    def test_load_rejects_invalid_status(self):
        invalid_ticket = self.tickets[0].copy()
        invalid_ticket["status"] = "pending"

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "status"):
            load_tickets(self.path)

    def test_load_rejects_invalid_category(self):
        invalid_ticket = {**self.tickets[0], "category": "Food"}

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "category"):
            load_tickets(self.path)

    def test_load_rejects_unhashable_category(self):
        invalid_ticket = {
            **self.tickets[0],
            "category": ["Network"],
        }

        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 1, "tickets": [invalid_ticket]},
                file,
            )

        with self.assertRaisesRegex(ValueError, "category"):
            load_tickets(self.path)

    def test_load_rejects_non_dictionary_ticket(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "schema_version": 1,
                    "tickets": ["not a valid ticket"],
                },
                file,
            )

        with self.assertRaisesRegex(ValueError, "dictionary"):
            load_tickets(self.path)

    def test_load_missing_file_returns_empty_list(self):
        missing_path = "data/file_that_does_not_exist.json"

        if os.path.exists(missing_path):
            os.remove(missing_path)

        self.assertEqual(load_tickets(missing_path), [])

    def test_load_rejects_malformed_json(self):
        with open(self.path, "w", encoding="utf-8") as file:
            file.write('{"schema_version": 1, "tickets": [}')

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            load_tickets(self.path)

    def test_load_rejects_unsupported_schema_version(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": 2, "tickets": []},
                file,
            )

        with self.assertRaisesRegex(
            ValueError, "unsupported or missing schema version"
        ):
            load_tickets(self.path)

    def test_load_rejects_boolean_schema_version(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": True, "tickets": []},
                file,
            )

        with self.assertRaisesRegex(
            ValueError, "unsupported or missing schema version"
        ):
            load_tickets(self.path)

    def test_load_rejects_non_list_tickets(self):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {
                    "schema_version": 1,
                    "tickets": "not a list",
                },
                file,
            )

        with self.assertRaisesRegex(ValueError, "list"):
            load_tickets(self.path)

    def test_generate_first_ticket_id(self):
        self.assertEqual(generate_ticket_id([]), "T001")

    def test_generate_next_ticket_id(self):
        tickets = [
            {"id": "T001"},
            {"id": "T005"},
            {"id": "T003"},
        ]

        self.assertEqual(generate_ticket_id(tickets), "T006")

    def test_ticket_ids_remain_unique_after_save_and_reload(self):
        save_tickets(self.tickets, self.path)
        loaded_tickets = load_tickets(self.path)

        next_id = generate_ticket_id(loaded_tickets)
        existing_ids = [ticket["id"] for ticket in loaded_tickets]

        self.assertNotIn(next_id, existing_ids)
        self.assertEqual(next_id, "T002")


def valid_ticket(ticket_id="T001", **overrides):
    ticket = {
        "id": ticket_id,
        "title": "Wi-Fi down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 12,
        "priority": "critical",
        "status": "open",
        "assigned_to": None,
        "notes": [],
    }
    ticket.update(overrides)
    return ticket


class TestStorageValidation(unittest.TestCase):

    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.path = os.path.join(temp_dir.name, "tickets.json")

    def write_raw(self, tickets, version=1):
        with open(self.path, "w", encoding="utf-8") as file:
            json.dump(
                {"schema_version": version, "tickets": tickets},
                file,
            )

    def test_v1_file_without_notes_loads_with_empty_notes(self):
        legacy = valid_ticket()
        del legacy["notes"]

        self.write_raw([legacy])

        self.assertEqual(load_tickets(self.path)[0]["notes"], [])

    def test_save_and_reload_preserves_notes_and_next_ids(self):
        notes = [
            {
                "note_id": "N001",
                "author": "A",
                "message": "first note",
            },
            {
                "note_id": "N002",
                "author": "B",
                "message": "second note",
            },
        ]

        save_tickets(
            [
                valid_ticket("T001", notes=notes),
                valid_ticket("T003"),
            ],
            self.path,
        )

        loaded = load_tickets(self.path)

        self.assertEqual(loaded[0]["notes"], notes)
        self.assertEqual(next_note_id(loaded[0]), "N003")
        self.assertEqual(generate_ticket_id(loaded), "T004")

    def test_duplicate_ticket_ids_rejected(self):
        self.write_raw(
            [valid_ticket("T001"), valid_ticket("T001")]
        )

        with self.assertRaisesRegex(ValueError, "duplicate ticket ID"):
            load_tickets(self.path)

    def test_invalid_records_are_rejected(self):
        bad_overrides = [
            {"category": "Banana"},
            {"category": "network"},
            {"urgency": "urgent"},
            {"affected_users": True},
            {"affected_users": 0},
            {"priority": "low"},
            {"status": "closed"},
            {"status": "in_progress", "assigned_to": None},
            {"assigned_to": "   "},
            {"id": "t001"},
            {"notes": "x"},
            {
                "notes": [
                    {
                        "note_id": "N001",
                        "author": "A",
                        "message": "hello world",
                    },
                    {
                        "note_id": "N001",
                        "author": "B",
                        "message": "another one",
                    },
                ]
            },
            {
                "notes": [
                    {
                        "note_id": "X1",
                        "author": "A",
                        "message": "hello world",
                    }
                ]
            },
            {
                "notes": [
                    {
                        "note_id": "N001",
                        "author": "",
                        "message": "hello world",
                    }
                ]
            },
            {
                "notes": [
                    {
                        "note_id": "N001",
                        "author": "A",
                        "message": "hey",
                    }
                ]
            },
            {
                "notes": [
                    {
                        "note_id": "N001",
                        "author": "A",
                    }
                ]
            },
        ]

        for overrides in bad_overrides:
            with self.subTest(overrides=overrides):
                self.write_raw([valid_ticket(**overrides)])

                with self.assertRaises(ValueError):
                    load_tickets(self.path)

    def test_missing_required_key_rejected(self):
        ticket = valid_ticket()
        del ticket["status"]

        self.write_raw([ticket])

        with self.assertRaisesRegex(ValueError, "missing keys"):
            load_tickets(self.path)

    def test_boolean_schema_version_rejected(self):
        self.write_raw([], version=True)

        with self.assertRaises(ValueError):
            load_tickets(self.path)

    def test_reload_into_keeps_memory_on_corrupt_json(self):
        memory = [valid_ticket("T009")]
        before = copy.deepcopy(memory)

        with open(self.path, "w", encoding="utf-8") as file:
            file.write('{"schema_version": 1, "tickets": [}')

        with self.assertRaises(ValueError):
            reload_into(memory, self.path)

        self.assertEqual(memory, before)

    def test_reload_into_keeps_memory_when_second_record_invalid(self):
        memory = [valid_ticket("T009")]
        before = copy.deepcopy(memory)

        self.write_raw(
            [
                valid_ticket("T001"),
                valid_ticket("T002", status="bogus"),
            ]
        )

        with self.assertRaises(ValueError):
            reload_into(memory, self.path)

        self.assertEqual(memory, before)

    def test_reload_into_replaces_memory_on_success(self):
        memory = [valid_ticket("T009")]

        self.write_raw([valid_ticket("T001")])

        reload_into(memory, self.path)

        self.assertEqual([ticket["id"] for ticket in memory], ["T001"])

    def test_failed_save_does_not_clobber_existing_file(self):
        save_tickets([valid_ticket("T001")], self.path)

        with open(self.path, encoding="utf-8") as file:
            good = file.read()

        with self.assertRaises(ValueError):
            save_tickets(
                [valid_ticket("T002", affected_users=0)],
                self.path,
            )

        with open(self.path, encoding="utf-8") as file:
            self.assertEqual(file.read(), good)

        self.assertEqual(
            os.listdir(os.path.dirname(self.path)),
            ["tickets.json"],
        )

    def test_generate_ticket_id_survives_a_record_without_id(self):
        self.assertEqual(
            generate_ticket_id([{"id": "T002"}, {}]),
            "T003",
        )


if __name__ == "__main__":
    unittest.main()
