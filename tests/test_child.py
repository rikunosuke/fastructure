import dataclasses
from datetime import datetime
from unittest import TestCase

from fastructure import structured


class TestChild(TestCase):
    def test_child(self):
        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Author:
            name: str
            age: int
            birthday: datetime

        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Book:
            title: str
            author: Author

        book = Book.from_dict(
            {
                "title": "Book",
                "author": {"name": "John", "age": 20, "birthday": datetime(2000, 1, 1)},
            }
        )

        self.assertEqual("Book", book.title)
        self.assertEqual("John", book.author.name)
        self.assertEqual(20, book.author.age)
        self.assertEqual(datetime(2000, 1, 1), book.author.birthday)

    def test_child_list(self):
        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Author:
            name: str
            age: int
            birthday: datetime

        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Book:
            title: str
            authors: list[Author]

        book = Book.from_dict(
            {
                "title": "Book",
                "authors": [
                    {
                        "name": "John",
                        "age": 20,
                        "birthday": datetime(2000, 1, 1),
                    },
                    {
                        "name": "Jessy",
                        "age": 22,
                        "birthday": datetime(2024, 1, 1),
                    },
                ],
            }
        )

        self.assertEqual("Book", book.title)
        self.assertListEqual(
            [
                Author("John", 20, datetime(2000, 1, 1)),
                Author("Jessy", 22, datetime(2024, 1, 1)),
            ],
            book.authors,
        )

    def test_child_tuple(self):
        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Author:
            name: str
            age: int
            birthday: datetime

        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Book:
            title: str
            authors: tuple[Author]

        book = Book.from_dict(
            {
                "title": "Book",
                "authors": (
                    {
                        "name": "John",
                        "age": 20,
                        "birthday": datetime(2000, 1, 1),
                    },
                    {
                        "name": "Jessy",
                        "age": 22,
                        "birthday": datetime(2024, 1, 1),
                    },
                ),
            }
        )

        self.assertEqual("Book", book.title)
        self.assertTupleEqual(
            (
                Author("John", 20, datetime(2000, 1, 1)),
                Author("Jessy", 22, datetime(2024, 1, 1)),
            ),
            book.authors,
        )

    def test_grand_child_list(self):
        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Location:
            name: str

        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Author:
            name: str
            age: int
            birthday: datetime
            is_from: Location

        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Book:
            title: str
            authors: list[Author]

        book = Book.from_dict(
            {
                "title": "Book",
                "authors": (
                    {
                        "name": "John",
                        "age": 20,
                        "birthday": datetime(2000, 1, 1),
                        "is_from": {"name": "Japan"},
                    },
                    {
                        "name": "Jessy",
                        "age": 22,
                        "birthday": datetime(2024, 1, 1),
                        "is_from": {"name": "U.S.A"},
                    },
                ),
            }
        )
        self.assertEqual("Book", book.title)
        self.assertListEqual(
            [
                Author("John", 20, datetime(2000, 1, 1), Location("Japan")),
                Author("Jessy", 22, datetime(2024, 1, 1), Location("U.S.A")),
            ],
            book.authors,
        )
