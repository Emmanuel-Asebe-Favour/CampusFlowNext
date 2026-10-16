from pathlib import Path

from campusflow.tickets import create_ticket, list_tickets, get_ticket_by_id
from campusflow.workflow import (
    assign_ticket,
    update_ticket_status,
    reopen_ticket,
)
from campusflow.storage import load_tickets, save_tickets
from campusflow.queue import display_queue
from campusflow.reports import display_report
from campusflow.notes import (
    get_notes,
    add_note
)


DATA_FILE = Path("data/tickets.json")


def save_data(tickets):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    save_tickets(tickets, DATA_FILE)


def find_ticket_or_raise(tickets, ticket_id):
    ticket = get_ticket_by_id(tickets, ticket_id)
    if ticket is None:
        raise ValueError("Unknown ticket ID: '{ticket_id}'.")
    return ticket


# def show_menu():
#     print("""
# \n===== CampusFlow Helpdesk =====")
#  1. Create ticket
# 2. List tickets
# 3. View ticket details
# 4. Assign ticket")
# 5. Update ticket status
# 6. Reopen resolved ticket
# 7. View unresolved queue
# 8. View report
# 0. Exit
# \n""")

def show_menu():
    print(
        "===== CampusFlow Helpdesk =====\n"
        "1. Create ticket\n"
        "2. List tickets\n"
        "3. View ticket details\n"
        "4. Assign ticket\n"
        "5. Update ticket status\n"
        "6. Reopen resolved ticket\n"
        "7. View unresolved queue\n"
        "8. View report\n"
        "9. Add note to \n"
        "10. View ticket notes\n"
        "0. Exit\n"
    )


def create_new_ticket(tickets):
    title = input("Ticket title: ")
    category = input("Category (Network/Hardware/Software/Other): ")
    urgency = input("Urgency (low/medium/high): ")
    affected_text = input("Number of affected users: ").strip()

    try:
        affected_users = int(affected_text)
        ticket = create_ticket(
            tickets, title, category, urgency, affected_users
        )
        tickets.append(ticket)
        save_data(tickets)
        print("Ticket created successfully: {ticket['id']}")
        print("Priority: {ticket['priority']}")
    except ValueError as error:
        print("Error: {error}")


def view_ticket(tickets):
    ticket_id = input("Ticket ID: ")
    ticket = find_ticket_or_raise(tickets, ticket_id)

    for key, value in ticket.items():
        print("{key.replace('_', ' ').title()}: {value}")


def assign_existing_ticket(tickets):
    ticket_id = input("Ticket ID: ").strip().upper()
    staff_name = input("Staff member name: ")

    ticket = assign_ticket(tickets, ticket_id, staff_name)
    save_data(tickets)
    print("{ticket['id']} assigned to {ticket['assigned_to']}.")


def change_status(tickets):
    ticket_id = input("Ticket ID: ").strip().upper()
    new_status = input(
        "New status (in_progress/resolved): "
    ).strip().lower()

    ticket = update_ticket_status(tickets, ticket_id, new_status)
    save_data(tickets)
    print("{ticket['id']} status is now {ticket['status']}.")


def reopen_resolved_ticket(tickets):
    ticket_id = input("Ticket ID to reopen: ").strip().upper()
    ticket = reopen_ticket(tickets, ticket_id)
    save_data(tickets)
    print("{ticket['id']} has been reopened.")


def main():
    try:
        tickets = load_tickets(DATA_FILE)
    except (ValueError, OSError) as error:
        print("Could not load saved tickets: {error}")
        return

    print("CampusFlow loaded {len(tickets)} ticket(s).")

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                create_new_ticket(tickets)

            elif choice == "2":
                list_tickets(tickets)

            elif choice == "3":
                view_ticket(tickets)

            elif choice == "4":
                assign_existing_ticket(tickets)

            elif choice == "5":
                change_status(tickets)

            elif choice == "6":
                reopen_resolved_ticket(tickets)

            elif choice == "7":
                display_queue(tickets)

            elif choice == "8":
                display_report(tickets)

            elif choice == "9":
                try:
                    ticket_id = input("Enter ticket ID: ")
                    author = input("Enter your name: ")
                    message = input("Enter note: ")
                    add_note(tickets, ticket_id, author, message)
                    print("Note added successfully")
                    save_data(tickets)
                except ValueError as e:
                    print(f"invalid Input {e}")

            elif choice == "10":
                try:
                    ticket_id = input("Enter ticket ID: ")
                    notes = get_notes(tickets, ticket_id)
                    if not notes:
                        print("No notes found for this ticket")
                    else:
                        for note in notes:
                            print(
                        f"{note['note_id']} - "
                        f"{note['author']} - "
                        f"{note['message']}"
                    )
                except ValueError as e:
                    print(f"Invalid Input: {e}")
                    
            elif choice == "0":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Enter a number from 0 to 8.")
        except (ValueError, OSError) as error:
            print("Error: {error}")


if __name__ == "__main__":
    main()
