import unittest

from lms.database import DatabaseManager
from lms.models import Book
from lms.reporting import LibraryReporter


class TestReporting(unittest.TestCase):
    def setUp(self):
        """Set up an in-memory database and reporter for testing."""
        self.db_manager = DatabaseManager(":memory:")
        self.db_manager.initialize_schema()
        self.reporter = LibraryReporter(self.db_manager)

        # Seed the database with some books
        self.db_manager.add_book(
            Book(
                title="The Hobbit",
                author="J.R.R Tolkien",
                isbn="978-0547928227",
            )
        )

        self.db_manager.add_book(
            Book(
                title="The Silmarillion",
                author="J.R.R Tolkien",
                isbn="978-0618397969",
            )
        )

        self.db_manager.add_book(
            Book(
                title="1984",
                author="J.R.R",
                isbn="978-0451524935",
            )
        )

    def test_search_books_by_title_returns_matches(self):
        """Test that searching by title returns a list of matching Book objects."""
        results = self.reporter.search_by_title("The")

        # We expect two matches by the title returns a list of matching Book objects.
        self.assertEqual(len(results), 2)
        titles = [book.title for book in results]
        self.assertIn("The Hobbit", titles)
        self.assertIn("The Silmarillion", titles)
        self.assertIsInstance(results[0], Book)

    def test_search_books_by_author_returns_matches(self):
        """Test that searching by author returns a list of matching Book objects."""
        # We expect two matches for "J.R.R Tolkiens"
        results = self.reporter.search_by_author("Tolkien")

        # Assert
        self.assertEqual(len(results), 2)
        authors = [book.author for book in results]
        self.assertIn("J.R.R Tolkien", authors)


if __name__ == "__main__":
    unittest.main()
