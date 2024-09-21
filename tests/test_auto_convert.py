import dataclasses
from datetime import datetime
from typing import Annotated
from unittest import TestCase

from fastructure import structured
from fastructure.typehints import AutoConvert


class TestAutoConvert(TestCase):
    def test_auto_convert(self):

        @structured(convert_all=False)
        @dataclasses.dataclass(frozen=True)
        class Author:
            name: str
            age: int
            birthday: Annotated[datetime, AutoConvert]

            @classmethod
            def clean_age(cls, age: int) -> int:
                assert isinstance(age, str), "age should not be converted to int"
                return age

        author = Author._construct(name="John", age="20", birthday="2000-01-01")
        self.assertEqual("John", author.name)
        self.assertEqual(
            "20",
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

            @staticmethod
            def clean_age(age: int) -> int:
                assert isinstance(age, int), "age should be converted to int"
                return age

            @classmethod
            def clean(cls, name: str, age: str) -> dict:
                assert isinstance(name, str)
                assert isinstance(age, str)
                return {"name": f"{name} (age {age})"}

        person = Person._construct(name="John", age="20", birthday="2000-01-01")
        self.assertEqual("John (age 20)", person.name)
        self.assertEqual(20, person.age)
        self.assertEqual(datetime(2000, 1, 1), person.birthday)
