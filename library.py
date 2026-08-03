"""
library.py
-----------
Core business logic for the Library Management System.

The `Library` class is the single point of contact between the user
interface (main.py) and the data layer (storage.py + models.py). It is
responsible for:
    * Book management        (add / update / delete / list)
    * Member management       (add / update / delete / list)
    * Issuing & returning books, with fine calculation
    * Search & filter across books and members
    * Enforcing all business rules and raising the appropriate
      custom exception whenever a rule is violated
"""

import re

import storage
from models import Book, Member, IssueRecord
from exceptions import (
    BookNotFoundError,
    MemberNotFoundError,
    DuplicateBookError,
    DuplicateMemberError,
    NoCopiesAvailableError,
    BookNotIssuedError,
    InvalidDataError,
    MembershipLimitError,
)

# A member may not have more than this many books out at once.
MAX_BOOKS_PER_MEMBER = 3

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class Library:
    def __init__(self):
        self._load_all()

    # ------------------------------------------------------------------ #
    # Persistence helpers
    # ------------------------------------------------------------------ #
    def _load_all(self):
        self.books = {
            b["book_id"]: Book.from_dict(b)
            for b in storage.load_json(storage.BOOKS_FILE, [])
        }
        self.members = {
            m["member_id"]: Member.from_dict(m)
            for m in storage.load_json(storage.MEMBERS_FILE, [])
        }
        self.issues = {
            r["record_id"]: IssueRecord.from_dict(r)
            for r in storage.load_json(storage.ISSUES_FILE, [])
        }

    def _save_books(self):
        storage.save_json(storage.BOOKS_FILE, [b.to_dict() for b in self.books.values()])

    def _save_members(self):
        storage.save_json(storage.MEMBERS_FILE, [m.to_dict() for m in self.members.values()])

    def _save_issues(self):
        storage.save_json(storage.ISSUES_FILE, [r.to_dict() for r in self.issues.values()])

    # ------------------------------------------------------------------ #
    # Validation helpers
    # ------------------------------------------------------------------ #
    @staticmethod
    def _require_non_empty(value, field_name):
        if value is None or str(value).strip() == "":
            raise InvalidDataError(f"{field_name} cannot be empty.")

    @staticmethod
    def _validate_email(email):
        if not EMAIL_REGEX.match(email or ""):
            raise InvalidDataError(f"'{email}' is not a valid email address.")

    # ------------------------------------------------------------------ #
    # Book Management
    # ------------------------------------------------------------------ #
    def add_book(self, title, author, isbn, category, total_copies=1):
        self._require_non_empty(title, "Title")
        self._require_non_empty(author, "Author")
        self._require_non_empty(isbn, "ISBN")
        try:
            total_copies = int(total_copies)
        except (ValueError, TypeError):
            raise InvalidDataError("Total copies must be a whole number.")
        if total_copies < 1:
            raise InvalidDataError("Total copies must be at least 1.")

        if any(b.isbn == isbn for b in self.books.values()):
            raise DuplicateBookError(f"A book with ISBN '{isbn}' already exists.")

        book_id = storage.next_id("book_id")
        book = Book(book_id, title.strip(), author.strip(), isbn.strip(),
                    category.strip() if category else "General", total_copies)
        self.books[book_id] = book
        self._save_books()
        return book

    def update_book(self, book_id, **fields):
        book = self.get_book(book_id)
        if "title" in fields and fields["title"]:
            book.title = fields["title"].strip()
        if "author" in fields and fields["author"]:
            book.author = fields["author"].strip()
        if "category" in fields and fields["category"]:
            book.category = fields["category"].strip()
        if "total_copies" in fields and fields["total_copies"] not in (None, ""):
            try:
                new_total = int(fields["total_copies"])
            except (ValueError, TypeError):
                raise InvalidDataError("Total copies must be a whole number.")
            issued_count = new_total - (new_total - book.available_copies)
            currently_issued = book.total_copies - book.available_copies
            if new_total < currently_issued:
                raise InvalidDataError(
                    f"Cannot set total copies below {currently_issued}: "
                    f"that many copies are currently issued."
                )
            book.available_copies = new_total - currently_issued
            book.total_copies = new_total
        self._save_books()
        return book

    def delete_book(self, book_id):
        book = self.get_book(book_id)
        if book.available_copies != book.total_copies:
            raise InvalidDataError(
                "Cannot delete a book that currently has copies issued out."
            )
        del self.books[book_id]
        self._save_books()

    def get_book(self, book_id):
        try:
            book_id = int(book_id)
        except (ValueError, TypeError):
            raise InvalidDataError("Book ID must be a number.")
        if book_id not in self.books:
            raise BookNotFoundError(f"No book found with ID {book_id}.")
        return self.books[book_id]

    def list_books(self):
        return sorted(self.books.values(), key=lambda b: b.book_id)

    # ------------------------------------------------------------------ #
    # Member Management
    # ------------------------------------------------------------------ #
    def add_member(self, name, email, phone):
        self._require_non_empty(name, "Name")
        self._require_non_empty(email, "Email")
        self._validate_email(email)

        if any(m.email.lower() == email.lower() for m in self.members.values()):
            raise DuplicateMemberError(f"A member with email '{email}' already exists.")

        member_id = storage.next_id("member_id")
        member = Member(member_id, name.strip(), email.strip(), (phone or "").strip())
        self.members[member_id] = member
        self._save_members()
        return member

    def update_member(self, member_id, **fields):
        member = self.get_member(member_id)
        if "name" in fields and fields["name"]:
            member.name = fields["name"].strip()
        if "email" in fields and fields["email"]:
            self._validate_email(fields["email"])
            member.email = fields["email"].strip()
        if "phone" in fields and fields["phone"]:
            member.phone = fields["phone"].strip()
        self._save_members()
        return member

    def delete_member(self, member_id):
        member = self.get_member(member_id)
        active_loans = [r for r in self.issues.values()
                         if r.member_id == member.member_id and not r.is_returned]
        if active_loans:
            raise InvalidDataError(
                "Cannot delete a member with books currently issued to them."
            )
        del self.members[member_id]
        self._save_members()

    def get_member(self, member_id):
        try:
            member_id = int(member_id)
        except (ValueError, TypeError):
            raise InvalidDataError("Member ID must be a number.")
        if member_id not in self.members:
            raise MemberNotFoundError(f"No member found with ID {member_id}.")
        return self.members[member_id]

    def list_members(self):
        return sorted(self.members.values(), key=lambda m: m.member_id)

    # ------------------------------------------------------------------ #
    # Issue & Return
    # ------------------------------------------------------------------ #
    def issue_book(self, book_id, member_id):
        book = self.get_book(book_id)
        member = self.get_member(member_id)

        if book.available_copies < 1:
            raise NoCopiesAvailableError(
                f"'{book.title}' has no available copies right now."
            )

        active_loans = [r for r in self.issues.values()
                         if r.member_id == member.member_id and not r.is_returned]
        if len(active_loans) >= MAX_BOOKS_PER_MEMBER:
            raise MembershipLimitError(
                f"{member.name} already has {MAX_BOOKS_PER_MEMBER} books issued "
                f"(the maximum allowed)."
            )
        if any(r.book_id == book.book_id for r in active_loans):
            raise InvalidDataError(f"{member.name} already has a copy of this book.")

        record_id = storage.next_id("record_id")
        record = IssueRecord(record_id, book.book_id, member.member_id)
        self.issues[record_id] = record
        book.available_copies -= 1

        self._save_issues()
        self._save_books()
        return record

    def return_book(self, book_id, member_id):
        book = self.get_book(book_id)
        member = self.get_member(member_id)

        record = next(
            (r for r in self.issues.values()
             if r.book_id == book.book_id and r.member_id == member.member_id
             and not r.is_returned),
            None,
        )
        if record is None:
            raise BookNotIssuedError(
                f"'{book.title}' is not currently issued to {member.name}."
            )

        from datetime import date
        record.return_date = date.today().isoformat()
        record.fine = record.calculate_fine()
        book.available_copies = min(book.total_copies, book.available_copies + 1)

        self._save_issues()
        self._save_books()
        return record

    def list_active_issues(self):
        return sorted(
            [r for r in self.issues.values() if not r.is_returned],
            key=lambda r: r.due_date,
        )

    def list_overdue_issues(self):
        return [r for r in self.list_active_issues() if r.is_overdue()]

    def list_all_issues(self):
        return sorted(self.issues.values(), key=lambda r: r.record_id)

    # ------------------------------------------------------------------ #
    # Search & Filter
    # ------------------------------------------------------------------ #
    def search_books(self, keyword=None, category=None, author=None,
                      available_only=False):
        results = list(self.books.values())
        if keyword:
            keyword = keyword.lower()
            results = [
                b for b in results
                if keyword in b.title.lower()
                or keyword in b.author.lower()
                or keyword in b.isbn.lower()
            ]
        if category:
            category = category.lower()
            results = [b for b in results if b.category.lower() == category]
        if author:
            author = author.lower()
            results = [b for b in results if author in b.author.lower()]
        if available_only:
            results = [b for b in results if b.available_copies > 0]
        return sorted(results, key=lambda b: b.title.lower())

    def search_members(self, keyword=None):
        results = list(self.members.values())
        if keyword:
            keyword = keyword.lower()
            results = [
                m for m in results
                if keyword in m.name.lower()
                or keyword in m.email.lower()
                or keyword in (m.phone or "").lower()
            ]
        return sorted(results, key=lambda m: m.name.lower())
