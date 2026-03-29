import unittest

from lms.main import LibraryApp


class TestLibraryApp(unittest.TestCase):
    def setUp(self) -> None:
        self.app = LibraryApp(db_path=":memory:")

    def test_register_user_successfully_saves_to_db(self):
        """Test that the app can register a new user."""
        username = "new_admin"
        password = "secure_password"

        # This method doesn't exist yet!
        self.app.register_user(username, password)

        # Verify the user exists in the database
        user = self.app.db_manager.get_user_by_username(username)
        self.assertIsNotNone(user)
        self.assertEqual(user.username, username)

    def test_borrow_book_successfully_saves_loan(self):
        """Test that the app can handle a user borrowing a book."""
        from lms.models import Book

        # Setup: Create a user and a book in our test database
        username = "borrower_test"
        isbn = "978-0123456789"
        book = Book(title="Test Book", author="Author", isbn=isbn)

        self.app.register_user(username, "password123")
        self.app.db_manager.add_book(book)

        # Action: Attempt to borrow the book
        self.app.borrow_book(username, isbn)

        # Assert: Check if the loan was actually saved
        loans = self.app.db_manager.get_loans_by_username(username)
        self.assertEqual(len(loans), 1)
        self.assertEqual(loans[0].isbn, isbn)
