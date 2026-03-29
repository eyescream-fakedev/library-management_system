"""
The Query Layer.
It handles specialized read-only operations, like searching for books by title or author.
"""

from lms.models import Book


class LibraryReporter:
    def __init__(self, db_manager) -> None:
        self.db_manager = db_manager

    def _map_rows_to_books(self, rows) -> list[Book]:
        """Helper method to convert database rows into Book objects"""
        return [
            Book(title=row["title"], author=row["author"], isbn=row["isbn"])
            for row in rows
        ]

    def search_by_title(self, title_query: str) -> list[Book]:
        """Searches for the books where the title contains the query string."""
        connection = self.db_manager.get_connection()

        # We use the SQL LIKE operator with % wildcards for partial matching
        query = "SELECT title,author,isbn FROM books WHERE title LIKE ?;"
        search_term = f"%{title_query}%"

        cursor = connection.execute(query, (search_term,))

        # Convert the raw database rows back into a list of Book objects
        return self._map_rows_to_books(cursor.fetchall())

    def search_by_author(self, author_query: str) -> list[Book]:
        connection = self.db_manager.get_connection()

        query = "SELECT title,author,isbn FROM books WHERE author LIKE ?;"
        search_term = f"%{author_query}%"

        cursor = connection.execute(query, (search_term,))

        # Convert the raw database rows back into a list of Book objects
        return self._map_rows_to_books(cursor.fetchall())
