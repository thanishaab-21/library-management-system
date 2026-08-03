"""
seed_data.py
-------------
Optional helper script that populates the library with a few sample books
and members so you have something to explore immediately after cloning the
repo, instead of starting from a completely empty system.

Run it once with:
    python seed_data.py
"""

from library import Library


def seed():
    lib = Library()

    if lib.books or lib.members:
        print("Data files already contain data — skipping seeding to avoid duplicates.")
        print("Delete the .json files inside data/ if you want to start fresh.")
        return

    sample_books = [
        ("The Pragmatic Programmer", "Andrew Hunt", "9780135957059", "Technology", 2),
        ("Clean Code", "Robert C. Martin", "9780132350884", "Technology", 3),
        ("A Brief History of Time", "Stephen Hawking", "9780553380163", "Science", 2),
        ("To Kill a Mockingbird", "Harper Lee", "9780061120084", "Fiction", 4),
        ("Sapiens", "Yuval Noah Harari", "9780062316097", "Non-Fiction", 2),
    ]
    for title, author, isbn, category, copies in sample_books:
        book = lib.add_book(title, author, isbn, category, copies)
        print(f"Added book: {book}")

    sample_members = [
        ("Asha Rao", "asha.rao@example.com", "9876543210"),
        ("Rahul Mehta", "rahul.mehta@example.com", "9123456780"),
    ]
    for name, email, phone in sample_members:
        member = lib.add_member(name, email, phone)
        print(f"Added member: {member}")

    print("\nSample data loaded successfully. Run 'python main.py' to start.")


if __name__ == "__main__":
    seed()
