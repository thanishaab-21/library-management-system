"""
test_library.py
-----------------
Unit tests for the Library Management System's core logic.

These tests run against a temporary, isolated data directory (via
monkeypatching storage's file paths) so they never touch or corrupt your
real library data.

Run with:
    python -m pytest tests/ -v
or, without pytest installed:
    python -m unittest discover tests
"""

import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import storage
from library import Library
from exceptions import (
    DuplicateBookError,
    DuplicateMemberError,
    BookNotFoundError,
    MemberNotFoundError,
    NoCopiesAvailableError,
    BookNotIssuedError,
    InvalidDataError,
    MembershipLimitError,
)


class LibraryTestCase(unittest.TestCase):
    def setUp(self):
        # Redirect all storage file paths to a fresh temp directory so
        # tests never touch real application data.
        self.tmp_dir = tempfile.mkdtemp()
        storage.DATA_DIR = self.tmp_dir
        storage.BOOKS_FILE = os.path.join(self.tmp_dir, "books.json")
        storage.MEMBERS_FILE = os.path.join(self.tmp_dir, "members.json")
        storage.ISSUES_FILE = os.path.join(self.tmp_dir, "issues.json")
        storage.COUNTERS_FILE = os.path.join(self.tmp_dir, "counters.json")
        self.lib = Library()

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # ---------------- Book management ----------------
    def test_add_book_success(self):
        book = self.lib.add_book("Dune", "Frank Herbert", "111", "Sci-Fi", 2)
        self.assertEqual(book.available_copies, 2)
        self.assertEqual(len(self.lib.list_books()), 1)

    def test_add_duplicate_isbn_raises(self):
        self.lib.add_book("Dune", "Frank Herbert", "111", "Sci-Fi", 2)
        with self.assertRaises(DuplicateBookError):
            self.lib.add_book("Dune Messiah", "Frank Herbert", "111", "Sci-Fi", 1)

    def test_add_book_empty_title_raises(self):
        with self.assertRaises(InvalidDataError):
            self.lib.add_book("", "Author", "222", "Fiction", 1)

    def test_get_nonexistent_book_raises(self):
        with self.assertRaises(BookNotFoundError):
            self.lib.get_book(9999)

    def test_delete_book_with_no_active_issues(self):
        book = self.lib.add_book("Dune", "Frank Herbert", "111", "Sci-Fi", 1)
        self.lib.delete_book(book.book_id)
        self.assertEqual(len(self.lib.list_books()), 0)

    # ---------------- Member management ----------------
    def test_add_member_success(self):
        member = self.lib.add_member("Asha Rao", "asha@example.com", "9999999999")
        self.assertEqual(len(self.lib.list_members()), 1)

    def test_add_member_invalid_email_raises(self):
        with self.assertRaises(InvalidDataError):
            self.lib.add_member("Asha Rao", "not-an-email", "9999999999")

    def test_add_duplicate_member_email_raises(self):
        self.lib.add_member("Asha Rao", "asha@example.com", "1")
        with self.assertRaises(DuplicateMemberError):
            self.lib.add_member("Someone Else", "asha@example.com", "2")

    def test_get_nonexistent_member_raises(self):
        with self.assertRaises(MemberNotFoundError):
            self.lib.get_member(9999)

    # ---------------- Issue & Return ----------------
    def test_issue_and_return_book(self):
        book = self.lib.add_book("Dune", "Frank Herbert", "111", "Sci-Fi", 1)
        member = self.lib.add_member("Asha Rao", "asha@example.com", "1")

        record = self.lib.issue_book(book.book_id, member.member_id)
        self.assertFalse(record.is_returned)
        self.assertEqual(self.lib.get_book(book.book_id).available_copies, 0)

        returned = self.lib.return_book(book.book_id, member.member_id)
        self.assertTrue(returned.is_returned)
        self.assertEqual(self.lib.get_book(book.book_id).available_copies, 1)

    def test_issue_no_copies_available_raises(self):
        book = self.lib.add_book("Dune", "Frank Herbert", "111", "Sci-Fi", 1)
        m1 = self.lib.add_member("Asha Rao", "asha@example.com", "1")
        m2 = self.lib.add_member("Rahul Mehta", "rahul@example.com", "2")

        self.lib.issue_book(book.book_id, m1.member_id)
        with self.assertRaises(NoCopiesAvailableError):
            self.lib.issue_book(book.book_id, m2.member_id)

    def test_return_book_not_issued_raises(self):
        book = self.lib.add_book("Dune", "Frank Herbert", "111", "Sci-Fi", 1)
        member = self.lib.add_member("Asha Rao", "asha@example.com", "1")
        with self.assertRaises(BookNotIssuedError):
            self.lib.return_book(book.book_id, member.member_id)

    def test_membership_limit_enforced(self):
        member = self.lib.add_member("Asha Rao", "asha@example.com", "1")
        for i in range(3):
            book = self.lib.add_book(f"Book {i}", "Author", f"ISBN-{i}", "Fiction", 1)
            self.lib.issue_book(book.book_id, member.member_id)

        extra_book = self.lib.add_book("Book Extra", "Author", "ISBN-extra", "Fiction", 1)
        with self.assertRaises(MembershipLimitError):
            self.lib.issue_book(extra_book.book_id, member.member_id)

    # ---------------- Search & Filter ----------------
    def test_search_books_by_keyword(self):
        self.lib.add_book("Dune", "Frank Herbert", "111", "Sci-Fi", 1)
        self.lib.add_book("Foundation", "Isaac Asimov", "222", "Sci-Fi", 1)
        results = self.lib.search_books(keyword="dune")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].title, "Dune")

    def test_search_books_available_only(self):
        b1 = self.lib.add_book("Dune", "Frank Herbert", "111", "Sci-Fi", 1)
        self.lib.add_book("Foundation", "Isaac Asimov", "222", "Sci-Fi", 1)
        member = self.lib.add_member("Asha Rao", "asha@example.com", "1")
        self.lib.issue_book(b1.book_id, member.member_id)

        results = self.lib.search_books(available_only=True)
        titles = [b.title for b in results]
        self.assertNotIn("Dune", titles)
        self.assertIn("Foundation", titles)


if __name__ == "__main__":
    unittest.main()
