import os
import sqlite3
import sys

# Add the src directory to the path so we can import our modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from lms.database import DatabaseManager
from lms.models import Book, User
from lms.reporting import LibraryReporter


class LibraryApp:
    def __init__(self, db_path: str = "libary.db") -> None:
        self.db_manager = DatabaseManager(db_path)
        self.db_manager.initialize_schema()
        self.reporter = LibraryReporter(self.db_manager)

    def display_menu(self) -> str:
        """Displays the main menu of the application."""
        options = [
            "1. Search & Borrow",
            "2. My Account (View/Return)",
            "3. Librarian Tools",
            "4. Exit",
        ]
        print("\n--- Library Management System---")
        for option in options:
            print(option)
        return input("Choose an option:  ")

    def run(self):
        while True:
            choice = self.display_menu()
            if choice == "1":
                self.search_borrow_menu()
            elif choice == "2":
                self.account_menu()
            elif choice == "3":
                self.librarian_menu()
            elif choice == "4":
                print("Goodbye")
                break
            else:
                print("Invalid option, Please try again.")

    def add_book_ui(self):
        """Allows a user to input a new book through the CLI."""
        print("\n--- Add a New Book ---")
        title = input("Title: ")
        author = input("Author: ")
        isbn = input("ISBN: ")

        try:
            # Step 1: Create Domain Object
            book = Book(title=title, author=author, isbn=isbn)

            # Step 2: Pass it to the Persistence Layer
            self.db_manager.add_book(book)
            print(f"Successfully added: {book}")

        except ValueError as e:
            # Catches our model validation (e.g empty title)
            print(f"Error: {e}")
        except sqlite3.IntegrityError:
            print(f"Error: A book with ISBN {isbn} already exists.")

    def search_by_title_ui(self):
        """Allows a user to search for a book by title through the CLI."""
        print("\n--- Search by Title ---")
        query = input("Enter the title (or part of the title: ")

        # Use Reporter to find matches
        results = self.reporter.search_by_title(query)

        if results:
            print(f"\nFound {len(results)} matches:")
            for book in results:
                print(f"- {book}")
        else:
            print("No book/s found matching that title.")

    def search_by_author_ui(self):
        """Allows a user to search for a book by author through the CLI."""
        print("\n--- Search by Author ---")
        query = input("Enter Author name (or part of name): ")

        # Use Reporter to find matches
        results = self.reporter.search_by_author(query)

        if results:
            print(f"\nFound {len(results)} matches:")
            for book in results:
                print(f"- {book}")
        else:
            print("No book/s found matching that Author.")

    def register_user_ui(self):
        print("\n--- Register New User ---")
        username = input("Username: ")
        password = input("Password: ")

        try:
            self.register_user(username=username, password=password)
            print(f"User {username} registered successfully!")
        except sqlite3.IntegrityError:
            print(f"Error: Username {username} is already taken.")

    def search_books_ui(self):
        """A sub-menu for different search types."""
        print("\n--- Search Books ---")
        print("1. Search by Title")
        print("2. Search by Author")
        print("3. Back to Main Menu")
        sub_choice = input("Choose a search type: ")

        if sub_choice == "1":
            self.search_by_title_ui()
        elif sub_choice == "2":
            self.search_by_author_ui()
        elif sub_choice == "3":
            return
        else:
            print("Invalid search type.")

    def borrow_book_ui(self):
        print("\n---- Borrow a Book ---")
        username = input("Enter your username: ")
        isbn = input("Enter the ISBN of the book: ")

        try:
            self.borrow_book(username=username, isbn=isbn)
            print(f"Successfully recorded loan for {username}")
        except sqlite3.IntegrityError:
            print("Error: Either the user or the ISBN does not exist.")

    def view_loans_ui(self):
        """Allows a user to view all their current loans through CLI."""
        print("\n--- My Borrowed Books ---")
        username = input("Enter your username:")

        books = self.db_manager.get_detailed_loans_by_username(username)

        if books:
            if len(books) > 1:
                print(f"\nUser '{username}' has {len(books)} books on loans:")
                for book in books:
                    print(f"- {book}")
            elif len(books) == 1:
                print(f"\n User '{username}' has 1 book on loans:")
                print(f"- {books[0]}")
        else:
            print(f"No active loans found for user '{username}'")

    def return_book_ui(self):
        print("\n--- Return a Book ---")
        username = input("Enter your username: ")
        isbn = input("Enter the ISBN of the book you're returning: ")

        self.db_manager.remove_loan(username=username, isbn=isbn)
        print(f"Successfully returned book {isbn} for user {username}.")

    def register_user(self, username, password):
        """Logic for registering a new user."""

        # Step 1:Create Domain Object
        user = User(username=username, password=password)
        # Step 2:Pass it to the Persistence Layer
        self.db_manager.add_user(user)

    def borrow_book(self, username, isbn):
        """
        Records a new loan for a user in the system.

        Args:
            username (str): The unique username of the person borrowing.
            isb (str): The unique ISBN of the book being borrowed.

        Raises:
            sqlite3.IntegrityError: If the username or ISBN does not exist in the database.
        """
        from lms.models import Loan

        # Step 1: Create a domain object
        loan = Loan(username=username, isbn=isbn)
        # Step 2: Pass it to the Persistence Layer
        self.db_manager.add_loan(loan)

    def librarian_menu(self):
        print("\n--- Librarian Tools ---")
        print("1. View All Registered Users")
        print("2. View All Books (with Status)")
        print("3. Add a New Book")
        print("4. Back to Main Menu")
        choice = input("Choose an option:")

        if choice == "1":
            self.view_all_users_ui()
        elif choice == "2":
            self.view_all_books_ui()
        elif choice == "3":
            self.add_book_ui()
        elif choice == "4":
            return

    def view_all_users_ui(self):
        print("\n--- All Registered Users ---")
        users = self.db_manager.get_all_users()
        for user in users:
            print(f"- {user.username}")

    def view_all_books_ui(self):
        print("\n--- Inventory Status ---")
        inventory = self.db_manager.get_books_with_status()
        for item in inventory:
            status_indicator = "[X]" if item["status"] == "Borrowed" else "[ ]"
            print(
                f"{status_indicator} {item['title']} by {item['author']} {item['isbn']}"
            )

    def search_borrow_menu(self):
        print("]n--- Search & Borrow ---")
        print("1. Search for a Book")
        print("2. Register as a New User")
        print("3. Borrow a Book")
        print("4. Back to Main Menu")
        choice = input("Choose an option: ")

        if choice == "1":
            self.search_books_ui()
        elif choice == "2":
            self.register_user_ui()
        elif choice == "3":
            self.borrow_book_ui()
        elif choice == "4":
            return

    def account_menu(self):
        print("\n--- My Account ---")
        print("1. View My Borrowed Books")
        print("2. Return a Book")
        print("3. Back to Main Menu")
        choice = input("Choose an option: ")

        if choice == "1":
            self.view_loans_ui()
        elif choice == "2":
            self.return_book_ui()
        elif choice == "3":
            return


if __name__ == "__main__":
    app = LibraryApp()
    app.run()
