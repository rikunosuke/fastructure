import dataclasses
from datetime import datetime
from unittest import TestCase

from fastructure import structured


class TestFromDic(TestCase):
    def test_from_dict(self):
        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Author:
            name: str
            age: int
            birthday: datetime

        author = Author.from_dict(
            {"name": "John", "age": 20, "birthday": datetime(2000, 1, 1)}
        )
        self.assertEqual("John", author.name)
        self.assertEqual(
            20,
            author.age,
            "if convert_all is False and AutoConvert is not annotated,"
            "then value should not be conveted",
        )
        self.assertEqual(datetime(2000, 1, 1), author.birthday)

        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Person:
            name: str
            age: int
            birthday: datetime

            @classmethod
            def dict_map(cls) -> dict:
                return {
                    "key-name": cls.name,
                    "key-age": cls.age,
                    "key-birthday": cls.birthday,
                }

        with self.assertRaises(Person.ValidationError):
            Person.from_dict(
                {"name": "John", "age": 20, "birthday": datetime(2000, 1, 1)}
            )

        person = Person.from_dict(
            {"key-name": "John", "key-age": "20", "key-birthday": "2000-01-01"}
        )
        self.assertEqual("John", person.name)
        self.assertEqual(20, person.age)
        self.assertEqual(datetime(2000, 1, 1), person.birthday)


class TestFromList(TestCase):
    def test_from_list_dict_map(self):
        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Author:
            name: str
            age: int
            birthday: datetime

        author = Author.from_list(["John", 20, datetime(2000, 1, 1)])
        self.assertEqual("John", author.name)
        self.assertEqual(20, author.age)
        self.assertEqual(datetime(2000, 1, 1), author.birthday)

        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Person:
            name: str
            age: int
            birthday: datetime

            @classmethod
            def clean_name(cls, first_name: str, last_name: str) -> str:
                return f"{first_name} {last_name}"

            @classmethod
            def list_map(cls) -> dict:
                return {0: "first_name", 1: "last_name", 2: cls.age, 3: cls.birthday}

        with self.assertRaises(Person.ValidationError):
            Person.from_list(["John", 20, datetime(2000, 1, 1)])

        person = Person.from_list(["John", "Doe", 20, "2000-01-01"])
        self.assertEqual("John Doe", person.name)
        self.assertEqual(20, person.age)
        self.assertEqual(datetime(2000, 1, 1), person.birthday)

    def test_from_list_list_map(self):
        @structured(convert_all=True)
        @dataclasses.dataclass(frozen=True)
        class Person:
            name: str
            age: int
            birthday: datetime

            @classmethod
            def clean_name(cls, first_name: str, last_name: str) -> str:
                return f"{first_name} {last_name}"

            @classmethod
            def list_map(cls) -> list:
                return ["first_name", "last_name", cls.age, cls.birthday]

        with self.assertRaises(Person.ValidationError):
            Person.from_list(["John", 20, datetime(2000, 1, 1)])

        person = Person.from_list(["John", "Doe", 20, "2000-01-01"])
        self.assertEqual("John Doe", person.name)
        self.assertEqual(20, person.age)
        self.assertEqual(datetime(2000, 1, 1), person.birthday)
