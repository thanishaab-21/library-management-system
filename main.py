"""
main.py
--------
Command-line interface for the Library Management System.

Run this file to start the application:
    python main.py

This module ONLY handles user interaction (menus, input, printing). All
actual logic and data validation lives in library.py / models.py, and all
persistence lives in storage.py. Every call into the Library object is
wrapped in a try/except so bad input or a business-rule violation is shown
to the user as a friendly message, and never crashes the program.
"""

import sys

from library import Library, MAX_BOOKS_PER_MEMBER
from exceptions import LibraryError


def pause():
    input("\nPress Enter to continue...")


def print_header(title):
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)


def read_int(prompt):
    value = input(prompt).strip()
    if not value.isdigit() and not (value.startswith("-") and value[1:].isdigit()):
        raise ValueError("Please enter a whole number.")
    return int(value)


# ---------------------------------------------------------------------- #
# Book Management Menu
# ---------------------------------------------------------------------- #
def menu_books(lib: Library):
    while True:
        print_header("BOOK MANAGEMENT")
        print("1. Add Book")
        print("2. View All Books")
        print("3. Update Book")
        print("4. Delete Book")
        print("5. Search / Filter Books")
        print("0. Back to Main Menu")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                title = input("Title: ")
                author = input("Author: ")
                isbn = input("ISBN: ")
                category = input("Category (e.g. Fiction, Science): ")
                copies = input("Number of copies [1]: ").strip() or "1"
                book = lib.add_book(title, author, isbn, category, copies)
                print(f"\n✔ Book added successfully: {book}")

            elif choice == "2":
                books = lib.list_books()
                print_header("ALL BOOKS")
                if not books:
                    print("No books in the library yet.")
                for b in books:
                    print(b)

            elif choice == "3":
                book_id = input("Book ID to update: ")
                print("Leave a field blank to keep it unchanged.")
                fields = {
                    "title": input("New title: ").strip() or None,
                    "author": input("New author: ").strip() or None,
                    "category": input("New category: ").strip() or None,
                    "total_copies": input("New total copies: ").strip() or None,
                }
                book = lib.update_book(book_id, **fields)
                print(f"\n✔ Book updated: {book}")

            elif choice == "4":
                book_id = input("Book ID to delete: ")
                lib.delete_book(book_id)
                print("\n✔ Book deleted successfully.")

            elif choice == "5":
                keyword = input("Keyword (title/author/ISBN, blank to skip): ").strip() or None
                category = input("Category filter (blank to skip): ").strip() or None
                available = input("Only show available copies? (y/N): ").strip().lower() == "y"
                results = lib.search_books(keyword=keyword, category=category,
                                            available_only=available)
                print_header(f"SEARCH RESULTS ({len(results)} found)")
                if not results:
                    print("No matching books found.")
                for b in results:
                    print(b)

            elif choice == "0":
                return
            else:
                print("Invalid option, please try again.")

        except LibraryError as e:
            print(f"\n✖ Error: {e}")
        except ValueError as e:
            print(f"\n✖ Invalid input: {e}")

        pause()


# ---------------------------------------------------------------------- #
# Member Management Menu
# ---------------------------------------------------------------------- #
def menu_members(lib: Library):
    while True:
        print_header("MEMBER MANAGEMENT")
        print("1. Add Member")
        print("2. View All Members")
        print("3. Update Member")
        print("4. Delete Member")
        print("5. Search Members")
        print("0. Back to Main Menu")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                name = input("Name: ")
                email = input("Email: ")
                phone = input("Phone: ")
                member = lib.add_member(name, email, phone)
                print(f"\n✔ Member added successfully: {member}")

            elif choice == "2":
                members = lib.list_members()
                print_header("ALL MEMBERS")
                if not members:
                    print("No members registered yet.")
                for m in members:
                    print(m)

            elif choice == "3":
                member_id = input("Member ID to update: ")
                print("Leave a field blank to keep it unchanged.")
                fields = {
                    "name": input("New name: ").strip() or None,
                    "email": input("New email: ").strip() or None,
                    "phone": input("New phone: ").strip() or None,
                }
                member = lib.update_member(member_id, **fields)
                print(f"\n✔ Member updated: {member}")

            elif choice == "4":
                member_id = input("Member ID to delete: ")
                lib.delete_member(member_id)
                print("\n✔ Member deleted successfully.")

            elif choice == "5":
                keyword = input("Search keyword (name/email/phone): ").strip() or None
                results = lib.search_members(keyword=keyword)
                print_header(f"SEARCH RESULTS ({len(results)} found)")
                if not results:
                    print("No matching members found.")
                for m in results:
                    print(m)

            elif choice == "0":
                return
            else:
                print("Invalid option, please try again.")

        except LibraryError as e:
            print(f"\n✖ Error: {e}")
        except ValueError as e:
            print(f"\n✖ Invalid input: {e}")

        pause()


# ---------------------------------------------------------------------- #
# Issue & Return Menu
# ---------------------------------------------------------------------- #
def menu_issue_return(lib: Library):
    while True:
        print_header("ISSUE & RETURN BOOKS")
        print(f"1. Issue a Book  (max {MAX_BOOKS_PER_MEMBER} per member)")
        print("2. Return a Book")
        print("3. View Active Issues")
        print("4. View Overdue Books")
        print("5. View All Issue Records")
        print("0. Back to Main Menu")
        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                book_id = input("Book ID to issue: ")
                member_id = input("Member ID: ")
                record = lib.issue_book(book_id, member_id)
                print(f"\n✔ Book issued successfully. Due back by {record.due_date}.")
                print(record)

            elif choice == "2":
                book_id = input("Book ID being returned: ")
                member_id = input("Member ID: ")
                record = lib.return_book(book_id, member_id)
                if record.fine > 0:
                    print(f"\n✔ Book returned. This book was overdue — "
                          f"fine due: ₹{record.fine:.2f}")
                else:
                    print("\n✔ Book returned on time. No fine due.")

            elif choice == "3":
                records = lib.list_active_issues()
                print_header(f"ACTIVE ISSUES ({len(records)})")
                if not records:
                    print("No books are currently issued out.")
                for r in records:
                    print(r)

            elif choice == "4":
                records = lib.list_overdue_issues()
                print_header(f"OVERDUE BOOKS ({len(records)})")
                if not records:
                    print("Nothing is overdue. 🎉")
                for r in records:
                    fine = r.calculate_fine()
                    print(f"{r}  | Fine so far: ₹{fine:.2f}")

            elif choice == "5":
                records = lib.list_all_issues()
                print_header(f"ALL ISSUE RECORDS ({len(records)})")
                if not records:
                    print("No issue records yet.")
                for r in records:
                    print(r)

            elif choice == "0":
                return
            else:
                print("Invalid option, please try again.")

        except LibraryError as e:
            print(f"\n✖ Error: {e}")
        except ValueError as e:
            print(f"\n✖ Invalid input: {e}")

        pause()


# ---------------------------------------------------------------------- #
# Main Menu
# ---------------------------------------------------------------------- #
def main():
    lib = Library()

    while True:
        print_header("LIBRARY MANAGEMENT SYSTEM")
        print("1. Book Management")
        print("2. Member Management")
        print("3. Issue & Return Books")
        print("4. Library Summary")
        print("0. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            menu_books(lib)
        elif choice == "2":
            menu_members(lib)
        elif choice == "3":
            menu_issue_return(lib)
        elif choice == "4":
            print_header("LIBRARY SUMMARY")
            print(f"Total books (titles) : {len(lib.books)}")
            print(f"Total copies         : {sum(b.total_copies for b in lib.books.values())}")
            print(f"Available copies     : {sum(b.available_copies for b in lib.books.values())}")
            print(f"Total members        : {len(lib.members)}")
            print(f"Books currently out   : {len(lib.list_active_issues())}")
            print(f"Overdue books         : {len(lib.list_overdue_issues())}")
            pause()
        elif choice == "0":
            print("\nGoodbye! 📚")
            sys.exit(0)
        else:
            print("Invalid option, please try again.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye! 📚")
        sys.exit(0)
    except Exception as e:
        # Last-resort safety net: even a totally unexpected error should
        # never dump a raw traceback in front of an end user.
        print(f"\n✖ A fatal unexpected error occurred: {e}")
        sys.exit(1)
