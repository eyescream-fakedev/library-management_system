"""
The Domain Layer of this system.
Defines the 'Blueprints' or 'Entities' of this system.
    Entities:
        Book, User, Loan classes.
"""

from typing import override

import bcrypt


class Book:
    """"""

    def __init__(self, title: str, author: str, isbn: str):
        if not title:
            raise ValueError("Title cannot be empty")
        self.title: str = title
        self.author: str = author
        self.isbn: str = isbn

    @override
    def __str__(self):
        return f"{self.title} by {self.author} (ISBN: {self.isbn})"


class User:
    def __init__(self, username: str, password: str):

        self.username: str = username
        self.password: bytes = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(),
        )

    def __str__(self):
        return self.username

    def verify_password(self, password: str) -> bool:
        input_password = password.encode("utf-8")
        return bcrypt.checkpw(input_password, self.password)


class Loan:
    def __init__(self, username: str, isbn: str) -> None:
        if not username:
            raise ValueError("Username cannot be empty")
        if not isbn:
            raise ValueError("ISBN cannot be empty")

        self.username = username
        self.isbn = isbn

    def __str__(self) -> str:
        return f"Loan: {self.username} has barrowed {self.isbn}"
