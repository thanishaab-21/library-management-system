"""
models.py
----------
Plain data-model classes for the Library Management System.

Each class knows how to turn itself into a dictionary (to_dict) and how to
rebuild itself from a dictionary (from_dict). That is the only piece of
"serialization awareness" the models need — the actual file I/O lives in
storage.py, keeping concerns cleanly separated.
"""

from datetime import datetime, date, timedelta

# Number of days a book may be borrowed before it is considered overdue.
LOAN_PERIOD_DAYS = 14
# Fine charged per day overdue (in rupees / your currency of choice).
FINE_PER_DAY = 5


class Book:
    def __init__(self, book_id, title, author, isbn, category,
                 total_copies=1, available_copies=None):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.category = category
        self.total_copies = total_copies
        # If not supplied (e.g. new book), all copies start out available.
        self.available_copies = (
            available_copies if available_copies is not None else total_copies
        )

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "isbn": self.isbn,
            "category": self.category,
            "total_copies": self.total_copies,
            "available_copies": self.available_copies,
        }

    @staticmethod
    def from_dict(data):
        return Book(
            book_id=data["book_id"],
            title=data["title"],
            author=data["author"],
            isbn=data["isbn"],
            category=data.get("category", "General"),
            total_copies=data.get("total_copies", 1),
            available_copies=data.get("available_copies", 1),
        )

    def __str__(self):
        return (f"[{self.book_id}] '{self.title}' by {self.author} "
                f"(ISBN: {self.isbn}, Category: {self.category}) | "
                f"Available: {self.available_copies}/{self.total_copies}")


class Member:
    def __init__(self, member_id, name, email, phone, membership_date=None):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.phone = phone
        self.membership_date = membership_date or date.today().isoformat()

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "membership_date": self.membership_date,
        }

    @staticmethod
    def from_dict(data):
        return Member(
            member_id=data["member_id"],
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            membership_date=data.get("membership_date"),
        )

    def __str__(self):
        return (f"[{self.member_id}] {self.name} | {self.email} | {self.phone} "
                f"| Member since: {self.membership_date}")


class IssueRecord:
    """Represents a single issue/return transaction for one book copy."""

    def __init__(self, record_id, book_id, member_id, issue_date=None,
                 due_date=None, return_date=None, fine=0.0):
        self.record_id = record_id
        self.book_id = book_id
        self.member_id = member_id
        self.issue_date = issue_date or date.today().isoformat()
        self.due_date = due_date or (
            date.today() + timedelta(days=LOAN_PERIOD_DAYS)
        ).isoformat()
        self.return_date = return_date
        self.fine = fine

    @property
    def is_returned(self):
        return self.return_date is not None

    def is_overdue(self, on_date=None):
        """Whether this loan is overdue as of `on_date` (defaults to today)."""
        check_date = on_date or date.today()
        due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
        if self.is_returned:
            returned = datetime.strptime(self.return_date, "%Y-%m-%d").date()
            return returned > due
        return check_date > due

    def calculate_fine(self, on_date=None):
        """Compute the fine owed based on how many days overdue the loan is."""
        check_date = on_date or date.today()
        due = datetime.strptime(self.due_date, "%Y-%m-%d").date()
        end_date = check_date
        if self.is_returned:
            end_date = datetime.strptime(self.return_date, "%Y-%m-%d").date()
        overdue_days = (end_date - due).days
        return max(0, overdue_days) * FINE_PER_DAY

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "book_id": self.book_id,
            "member_id": self.member_id,
            "issue_date": self.issue_date,
            "due_date": self.due_date,
            "return_date": self.return_date,
            "fine": self.fine,
        }

    @staticmethod
    def from_dict(data):
        return IssueRecord(
            record_id=data["record_id"],
            book_id=data["book_id"],
            member_id=data["member_id"],
            issue_date=data.get("issue_date"),
            due_date=data.get("due_date"),
            return_date=data.get("return_date"),
            fine=data.get("fine", 0.0),
        )

    def __str__(self):
        status = f"Returned on {self.return_date}" if self.is_returned else "Not returned"
        overdue = " (OVERDUE)" if self.is_overdue() and not self.is_returned else ""
        return (f"[{self.record_id}] Book:{self.book_id} Member:{self.member_id} "
                f"Issued:{self.issue_date} Due:{self.due_date} | {status}{overdue}")
