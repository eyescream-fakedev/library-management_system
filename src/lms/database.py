"""
The Persistance Layer.
It handles the 'Translation' between raw SQL rows and the objects.
"""

import sqlite3


class DatabaseManager:
    def __init__(self, db_path):
        if not db_path:
            raise ValueError("Database path cannot be empty.")
        self.db_path: str = db_path
        self._connection = None

    def get_connection(self):
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_path)
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA foreign_keys = ON;")
        return self._connection

    def initialize_schema(self):
        connection = self.get_connection()

        schema = """
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password BLOB NOT NULL
        );

        CREATE TABLE IF NOT EXISTS loans(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        isbn TEXT NOT NULL,
        FOREIGN KEY (username) REFERENCES users(username),
        FOREIGN KEY (isbn) REFERENCES books(isbn)
        );
        """

        try:
            connection.executescript(schema)
            connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            connection.rollback()

    def add_book(self, book):
        """Adds a Book object to the database."""
        connection = self.get_connection()
        query = "INSERT INTO books (title,author,isbn) VALUES (?,?,?);"
        connection.execute(query, (book.title, book.author, book.isbn))
        connection.commit()

    def get_book_by_isbn(self, isbn):
        from lms.models import Book

        connection = self.get_connection()
        query = "SELECT title, author, isbn FROM books WHERE isbn=?;"
        cursor = connection.execute(query, (isbn,))
        result = cursor.fetchone()

        if result:
            return Book(
                title=result["title"],
                author=result["author"],
                isbn=result["isbn"],
            )
        return None

    def add_user(self, user):
        """Adds a User object to the database."""
        connection = self.get_connection()
        query = "INSERT INTO users (username,password) VALUES (?,?);"

        connection.execute(query, (user.username, user.password))
        connection.commit()

    def get_user_by_username(self, username: str):
        from lms.models import User

        connection = self.get_connection()
        query = "SELECT username, password FROM users WHERE username=?;"
        cursor = connection.execute(query, (username,))
        result = cursor.fetchone()

        if result:
            # Create the User object
            user = User(username=result["username"], password="placeholder")
            user.password = result["password"]
            return user
        return None

    def add_loan(self, loan):
        """Adds a Loan object to the database."""
        connection = self.get_connection()
        query = "INSERT INTO loans (username, isbn) VALUES (?,?);"

        try:
            connection.execute(query, (loan.username, loan.isbn))
            connection.commit()
        except sqlite3.IntegrityError as e:
            connection.rollback()
            raise e

    def get_loans_by_username(self, username):
        from lms.models import Loan

        connection = self.get_connection()
        query = "SELECT username, isbn FROM loans WHERE username=?;"
        cursor = connection.execute(query, (username,))
        rows = cursor.fetchall()

        # Map each row to a Loan object
        return [Loan(username=row["username"], isbn=row["isbn"]) for row in rows]

    def get_detailed_loans_by_username(self, username: str):
        from lms.models import Book

        connection = self.get_connection()

        query = """
            SELECT books.title,books.author,books.isbn
            FROM loans
            JOIN books on loans.isbn = books.isbn
            WHERE loans.username=?;
        """

        cursor = connection.execute(query, (username,))
        rows = cursor.fetchall()

        # Step 2: Map each row back into a full Book object
        return [
            Book(title=row["title"], author=row["author"], isbn=row["isbn"])
            for row in rows
        ]

    def remove_loan(self, username: str, isbn: str):
        """Removes a Loan record from the database."""
        connection = self.get_connection()
        query = "DELETE FROM loans WHERE username=? AND isbn=?;"

        connection.execute(query, (username, isbn))
        connection.commit()

    def get_all_users(self):
        """
        Get all the users from the database.

        Returns:
            list of User objects.
        """
        from lms.models import User

        connection = self.get_connection()
        query = "SELECT username, password FROM users;"
        cursor = connection.execute(query)
        rows = cursor.fetchall()

        users = []
        for row in rows:
            user = User(username=row["username"], password="placeholder")
            user.password = row["password"]
            users.append(user)
        return users

    def get_books_with_status(self) -> list:
        connection = self.get_connection()

        query = """
            SELECT
                books.title,
                books.author,
                books.isbn,
                CASE
                    WHEN loans.isbn is NULL THEN 'Available'
                    ELSE "Borrowed"
                END as status
            FROM books
            LEFT JOIN loans ON books.isbn = loans.isbn;
        """

        cursor = connection.execute(query)
        return cursor.fetchall()
