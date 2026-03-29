import unittest

import bcrypt

from lms.models import Book, Loan, User


class TestBook(unittest.TestCase):
    def test_book_initialization(self):
        """Test that a Book object can be initialized with a title, author, and ISBN."""
        book = Book(title="The Hobbit", author="J.R.R Tolkien", isbn="978-0547928227")
        self.assertEqual(book.title, "The Hobbit")
        self.assertEqual(book.author, "J.R.R Tolkien")
        self.assertEqual(book.isbn, "978-0547928227")

    def test_book_string_representation(self):
        """Test that a Book object has a clean string representation."""
        book = Book(title="The Hobbit", author="J.R.R Tolkien", isbn="978-0547928227")

        self.assertEqual(
            str(book), "The Hobbit by J.R.R Tolkien (ISBN: 978-0547928227)"
        )

    def test_book_initialization_with_empty_title_raises_error(self):
        """Test that initializing a Book with an empty title raises a ValueError."""
        with self.assertRaises(ValueError):
            Book(title="", author="J.R.R Tolkien", isbn="978-0547928227")


class TestUser(unittest.TestCase):
    def test_user_initialization_hashes_password(self):
        """Test that a User object hashes its password upon initialization."""
        raw_password = "secure_password"
        user = User(username="jdoe", password=raw_password)

        # The password stored should not be the raw password
        self.assertNotEqual(user.password, raw_password)

        # Verify it's a valid bcrypt hash
        self.assertTrue(
            bcrypt.checkpw(
                raw_password.encode("utf-8"),
                user.password,
            )
        )

    def test_verify_password_returns_true_for_correct_password(self):
        """Test that the verify_password method returns True for the correct password."""
        user = User(username="jdoe", password="secure_password")
        self.assertTrue(user.verify_password("secure_password"))

    def test_verify_password_returns_false_for_incorrect_password(self):
        """Test that the verify_password method returns False for an incorrect password"""
        user = User(username="jdoe", password="secure_password")
        self.assertFalse(user.verify_password("wrong_password"))


class TestLoan(unittest.TestCase):
    def test_loan_creation_with_valid_attributes(self):
        """Test that a loan object can be created with a username and ISBN."""

        username = "borrower_user"
        isbn = "978-0547928227"

        loan = Loan(username=username, isbn=isbn)

        self.assertEqual(loan.username, username)
        self.assertEqual(loan.isbn, isbn)


if __name__ == "__main__":
    unittest.main()
