import sqlite3
import unittest

import bcrypt

from lms.database import DatabaseManager
from lms.models import Book, Loan, User


class TestDatabase(unittest.TestCase):
    def setUp(self):
        """Set up an in-memory database for testing."""
        self.db_name = ":memory:"
        self.db_manager = DatabaseManager(self.db_name)

    def test_database_connection(self):
        """Test that the database connection is successfully established and uses sqlite3.Row."""
        connection = self.db_manager.get_connection()
        self.assertIsInstance(connection, sqlite3.Connection)
        self.assertEqual(connection.row_factory, sqlite3.Row)

    def test_foreign_keys_enabled(self):
        """Test that foreign keys are explicitly enabled."""
        connection = self.db_manager.get_connection()
        cursor = connection.execute("PRAGMA foreign_keys;")
        result = cursor.fetchone()
        self.assertEqual(result[0], 1)

    def test_schema_initialization_creates_books_tables(self):
        """Test that the 'books' table is created during initialization."""
        self.db_manager.initialize_schema()
        connection = self.db_manager.get_connection()
        cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='books';"
        )
        result = cursor.fetchone()
        self.assertIsNotNone(result)

    def test_add_book_saves_to_database(self):
        """Test that a Book object can be added to the database."""
        self.db_manager.initialize_schema()
        book = Book(title="The Hobbit", author="J.R.R Tolkien", isbn="978-0547928227")
        self.db_manager.add_book(book)

        connection = self.db_manager.get_connection()
        cursor = connection.execute(
            "SELECT title, author, isbn FROM books WHERE isbn='978-0547928227';"
        )
        row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["title"], "The Hobbit")
        self.assertEqual(row["author"], "J.R.R Tolkien")

    def test_add_duplicates_isbn_integrity_error(self):
        """Test that adding a book with duplicate ISBN raises an sqlite3.IntegrityError."""
        self.db_manager.initialize_schema()

        book1 = Book(
            title="The Hobbit",
            author="J.R.R Tolkien",
            isbn="978-0547928227",
        )
        book2 = Book(
            title="The Fellowship of the Ring",
            author="J.R.R Tolkien",
            isbn="978-0547928227",
        )

        self.db_manager.add_book(book1)
        with self.assertRaises(sqlite3.IntegrityError):
            self.db_manager.add_book(book2)

    def test_get_book_by_isbn_return_correct_book(self):
        """Test that a Book object can be retrieved from the database by ISBN."""
        self.db_manager.initialize_schema()
        book = Book(
            title="The Hobbit",
            author="J.R.R Tolkien",
            isbn="978-0547928227",
        )

        self.db_manager.add_book(book)
        retrieved_book: Book = self.db_manager.get_book_by_isbn("978-0547928227")  # pyright: ignore[reportAssignmentType]

        self.assertIsNotNone(retrieved_book)
        self.assertEqual(retrieved_book.title, "The Hobbit")
        self.assertEqual(retrieved_book.author, "J.R.R Tolkien")
        self.assertEqual(retrieved_book.isbn, "978-0547928227")

    def test_schema_initialization_creates_users_table(self):
        """Test that the 'users' table is created during initialization."""
        self.db_manager.initialize_schema()
        connection = self.db_manager.get_connection()
        cursor = connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users';"
        )
        result = cursor.fetchone()

        self.assertIsNotNone(
            result, "The 'users' table should exist after initialization."
        )

    def test_add_user_saves_to_database(self):
        """Test that a User object can be added to the database."""
        self.db_manager.initialize_schema()
        user = User(username="testuser", password="secure_password")

        self.db_manager.add_user(user)

        connection = self.db_manager.get_connection()
        cursor = connection.execute(
            "SELECT username,password FROM users WHERE username='testuser';"
        )
        row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["username"], "testuser")
        self.assertIsInstance(row["password"], bytes)
        self.assertTrue(
            bcrypt.checkpw("secure_password".encode("utf-8"), row["password"])
        )

    def test_get_user_by_username_returns_correct_user(self):
        """Test that a User object can be retrieved from the database by username."""
        self.db_manager.initialize_schema()

        # Create and save a user first
        user = User(username="auth_user", password="secret_password")
        self.db_manager.add_user(user)

        # Attempt to retrieve them
        retrieved_user = self.db_manager.get_user_by_username("auth_user")

        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.username, "auth_user")
        self.assertTrue(retrieved_user.verify_password("secret_password"))

    def test_add_loan_saves_to_database(self):
        """Test that a Loan object can be added to the database."""
        self.db_manager.initialize_schema()

        # Setup: Foreign keys require the user and book to exist first
        user = User(username="borrower", password="password123")
        book = Book(title="1984", author="George Orwell", isbn="1234567890")
        self.db_manager.add_user(user)
        self.db_manager.add_book(book)

        # Action: Create and add the loan
        loan = Loan(username="borrower", isbn="1234567890")
        self.db_manager.add_loan(loan)

        # Verification: CHeck the persistence layer
        connection = self.db_manager.get_connection()
        cursor = connection.execute(
            "SELECT username, isbn FROM loans WHERE username='borrower';"
        )

        row = cursor.fetchone()

        self.assertIsNotNone(row)
        self.assertEqual(row["username"], "borrower")
        self.assertEqual(row["isbn"], "1234567890")

    def test_get_loans_by_username_returns_list_of_loans(self):
        """Test that all loans for a specific user can be retrieved."""
        self.db_manager.initialize_schema()

        # Setup: Create a user and two books
        user = User(username="reader1", password="password")
        book1 = Book(author="Book One", title="Author A", isbn="ISBN1")
        book2 = Book(author="Book Two", title="Author B", isbn="ISBN2")
        self.db_manager.add_user(user)
        self.db_manager.add_book(book1)
        self.db_manager.add_book(book2)

        # Action: Create two loans for this user
        self.db_manager.add_loan(Loan(username="reader1", isbn="ISBN1"))
        self.db_manager.add_loan(Loan(username="reader1", isbn="ISBN2"))

        # Retrieval
        loans = self.db_manager.get_loans_by_username("reader1")

        # Assert
        self.assertEqual(len(loans), 2)
        self.assertEqual(loans[0].isbn, "ISBN1")
        self.assertEqual(loans[1].isbn, "ISBN2")
        self.assertIsInstance(loans[0], Loan)

    def test_get_loan_details_Returns_book_info(self):
        """Test that we can retrieve full book details for a user's loan."""
        self.db_manager.initialize_schema()

        # Setup: Create a user and a book
        user = User(username="reader1", password="password")
        book = Book(
            title="The Great Gatsby", author="F. Scott Fitzgerald", isbn="GATSBY"
        )
        self.db_manager.add_user(user)
        self.db_manager.add_book(book)
        self.db_manager.add_loan(Loan(username="reader1", isbn="GATSBY"))

        # Action: Call a new method to get detailed loans.
        detailed_loans = self.db_manager.get_detailed_loans_by_username("reader1")

        # Verification: We should get back a list of Book objects.
        self.assertEqual(len(detailed_loans), 1)
        self.assertEqual(detailed_loans[0].title, "The Great Gatsby")
        self.assertEqual(detailed_loans[0].author, "F. Scott Fitzgerald")

    def test_remove_loan_deletes_record_from_database(self):
        """Test that removing a loan correctly deletes it from the database."""
        self.db_manager.initialize_schema()

        # Setup: Create a user, book, and a loan
        user = User(username="returner", password="password")
        book = Book(title="The Odyssey", author="Homer", isbn="ODYSSEY")
        self.db_manager.add_user(user)
        self.db_manager.add_book(book)
        self.db_manager.add_loan(Loan(username="returner", isbn="ODYSSEY"))

        # Action: Remove the loan
        self.db_manager.remove_loan(username="returner", isbn="ODYSSEY")
        loans = self.db_manager.get_loans_by_username(username="returner")

        # Verification: Check that the loan is gone
        self.assertEqual(len(loans), 0)

    def test_get_all_users_returns_list_of_users(self):
        """Test that we can retrieve a list of all registered users."""
        self.db_manager.initialize_schema()

        # Setup: Add two users
        self.db_manager.add_user(User(username="admin", password="password"))
        self.db_manager.add_user(User(username="librarian", password="password"))

        # Action: Retrieve all users
        users = self.db_manager.get_all_users()

        # Verification: check how many users, if its an User object and check the username
        self.assertEqual(len(users), 2)
        self.assertIsInstance(users[0], User)
        self.assertEqual(users[0].username, "admin")

    def test_get_books_with_status_correctly_identifies_availability(self):
        """Test that we can retrieve books with a their current loan status."""
        self.db_manager.initialize_schema()

        # Setup: Create two books
        self.db_manager.add_book(
            Book(
                title="Available Book",
                author="Author",
                isbn="ISBN-AVAIL",
            )
        )
        self.db_manager.add_book(
            Book(
                title="Borrowed Book",
                author="Author",
                isbn="ISBN-BORROW",
            )
        )

        user = User(username="borrower", password="password")
        self.db_manager.add_user(user)
        self.db_manager.add_loan(
            Loan(
                username=user.username,
                isbn="ISBN-BORROW",
            )
        )

        # Action: Retrieve all books with status
        results = self.db_manager.get_books_with_status()

        # Verification: Results should be a list of tuples or dicts
        self.assertEqual(len(results), 2)

        # Find the borrowed book in the results
        borrowed = next(r for r in results if r["isbn"] == "ISBN-BORROW")
        self.assertEqual(borrowed["status"], "Borrowed")
        # Find the the available book in the results
        available = next(r for r in results if r["isbn"] == "ISBN-AVAIL")
        self.assertEqual(available["status"], "Available")


if __name__ == "__main__":
    unittest.main()
