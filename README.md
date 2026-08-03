# 📚 Library Management System

A Python command-line application for managing books, members, and book
issue/return records in a library. Built as an internship project to
demonstrate object-oriented design, file-based data persistence, and
robust exception handling.

---

## ✨ Features

| Feature | Description |
|---|---|
| **Book Management** | Add, view, update, and delete books. Each book tracks title, author, ISBN, category, total copies, and available copies. |
| **Member Management** | Register, view, update, and delete library members with name, email, and phone number. |
| **Issue & Return Books** | Issue a book to a member (enforcing a 3-book limit per member and copy availability), return books, and automatically calculate overdue fines. |
| **Search & Filter** | Search books by title/author/ISBN keyword, filter by category or availability. Search members by name/email/phone. |
| **Data Storage** | All data is persisted locally as JSON files (`data/books.json`, `data/members.json`, `data/issues.json`) — no external database required. Writes are atomic to prevent data corruption. |
| **Exception Handling** | Custom exception hierarchy (`exceptions.py`) cleanly separates business-rule violations (e.g. "no copies available", "duplicate ISBN") from input errors and storage errors, so the app never crashes on bad input. |

---

## 🗂️ Project Structure

```
library-management-system/
├── main.py            # CLI entry point — menus and user interaction
├── library.py          # Core business logic (Library class)
├── models.py           # Data models: Book, Member, IssueRecord
├── storage.py          # JSON file read/write layer (persistence)
├── exceptions.py        # Custom exception classes
├── seed_data.py         # Optional script to pre-populate sample data
├── requirements.txt      # Python dependencies (only needed for tests)
├── data/               # JSON data files (auto-created at runtime)
├── tests/
│   └── test_library.py   # Automated unit tests
├── LICENSE
└── README.md
```

### Why this structure?

The project follows a simple layered design:

1. **`models.py`** — plain data classes with no logic beyond
   serialization (`to_dict` / `from_dict`).
2. **`storage.py`** — the only file that touches the file system. It
   knows nothing about books or members, only about reading/writing JSON
   safely.
3. **`library.py`** — the brain of the app. Enforces every business rule
   (no duplicate ISBNs, max 3 books per member, can't delete a book that's
   currently on loan, etc.) and raises a specific exception when a rule is
   broken.
4. **`main.py`** — a thin CLI layer that just displays menus, collects
   input, and prints results or friendly error messages.

This separation means the core logic in `library.py` could be reused
as-is behind a web API or GUI in the future without any changes.

---

## ⚙️ Requirements

- Python 3.8 or higher (no external packages needed to run the app)
- `pytest` only if you want to run the automated test suite

Check your Python version:
```bash
python3 --version
```

---

## 🚀 How to Run

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/library-management-system.git
   cd library-management-system
   ```

2. **(Optional) Load sample data** so you have some books/members to try
   right away:
   ```bash
   python3 seed_data.py
   ```

3. **Run the application**
   ```bash
   python3 main.py
   ```

4. **Use the menus.** For example, to try the full flow:
   - Choose `1` → `1` to add a new book
   - Choose `2` → `1` to register a new member
   - Choose `3` → `1` to issue a book to that member
   - Choose `3` → `2` to return it later

Your data is automatically saved to the `data/` folder as JSON after
every change, so it will still be there the next time you run the app.

### Running the automated tests

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

All 15 tests should pass, covering book management, member management,
issuing/returning, business-rule enforcement, and search/filter.

---

## 🖥️ Example Session

```
============================================================
                 LIBRARY MANAGEMENT SYSTEM
============================================================
1. Book Management
2. Member Management
3. Issue & Return Books
4. Library Summary
0. Exit
Choose an option: 3

============================================================
                    ISSUE & RETURN BOOKS
============================================================
1. Issue a Book  (max 3 per member)
2. Return a Book
3. View Active Issues
4. View Overdue Books
5. View All Issue Records
0. Back to Main Menu
Choose an option: 1
Book ID to issue: 1
Member ID: 1

✔ Book issued successfully. Due back by 2026-08-15.
[1] Book:1 Member:1 Issued:2026-08-01 Due:2026-08-15 | Not returned
```

---

## 🧠 Business Rules Enforced

- A book cannot be issued if it has zero available copies
  (`NoCopiesAvailableError`).
- A member cannot have more than **3 books** issued at the same time
  (`MembershipLimitError`).
- A book cannot be added twice with the same ISBN
  (`DuplicateBookError`).
- A member cannot be registered twice with the same email
  (`DuplicateMemberError`).
- A book cannot be deleted while copies of it are currently issued out.
- A member cannot be deleted while they still have books issued to them.
- Returning a book that was never issued to that member raises
  `BookNotIssuedError`.
- Books are due back **14 days** after issue; returning late incurs a
  fine of **₹5/day** overdue, calculated automatically.

---

## 🛣️ Possible Future Enhancements

- Web interface using Flask/Django
- Email/SMS reminders for due/overdue books
- Multi-user login with librarian vs. member roles
- Migrate storage from JSON files to SQLite/PostgreSQL for larger
  libraries

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE)
for details.

---

## 👤 Author

**Thanishaa B**
Built as an internship project — Task 2: Library Management System.
