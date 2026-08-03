"""
exceptions.py
--------------
Custom exception classes used across the Library Management System.

Using dedicated exception types (instead of generic Exception/ValueError
everywhere) makes error handling in main.py precise and makes the code
self-documenting: the name of the exception tells you exactly what went
wrong.
"""


class LibraryError(Exception):
    """Base class for all custom exceptions raised by this application."""
    pass


class BookNotFoundError(LibraryError):
    """Raised when a book with the given ID/ISBN does not exist."""
    pass


class MemberNotFoundError(LibraryError):
    """Raised when a member with the given ID does not exist."""
    pass


class DuplicateBookError(LibraryError):
    """Raised when trying to add a book whose ISBN already exists."""
    pass


class DuplicateMemberError(LibraryError):
    """Raised when trying to add a member whose ID/email already exists."""
    pass


class NoCopiesAvailableError(LibraryError):
    """Raised when trying to issue a book that has zero available copies."""
    pass


class BookNotIssuedError(LibraryError):
    """Raised when trying to return a book that was never issued to that member."""
    pass


class InvalidDataError(LibraryError):
    """Raised when input data fails validation (empty fields, bad types, etc.)."""
    pass


class MembershipLimitError(LibraryError):
    """Raised when a member has reached the maximum number of books they may borrow."""
    pass


class StorageError(LibraryError):
    """Raised when reading from or writing to the JSON data files fails."""
    pass
