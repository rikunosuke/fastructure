import dataclasses
from datetime import datetime, timedelta
from functools import singledispatchmethod
from typing import Annotated
from unittest import TestCase

from fastructure import structured
from fastructure.typehints import AutoConvert


class TestMethodKwargs(TestCase):
    def test_only_one_arg(self):
        """
        Test that the method with only one argument is called correctly.
        :return:
        """

        @structured()
        @dataclasses.dataclass(frozen=True, kw_only=True)
        class Author:
            name: str
            age: int
            debut_year: int
            birthday: datetime

            @classmethod
            def clean_name(cls, name: str) -> str:
                return name.strip()

            @staticmethod
            def clean_age(age: int) -> int:
                return age + 1

            @singledispatchmethod
            @staticmethod
            def clean_debut_year(debut_year: int) -> int:
                return debut_year + 1

            @clean_debut_year.register
            @staticmethod
            def _(debut_year: str) -> int:
                return int(debut_year)

            @singledispatchmethod
            @classmethod
            def clean_birthday(cls, birthday: datetime) -> datetime:
                return birthday + timedelta(days=1)

            @clean_birthday.register
            @classmethod
            def _(cls, birthday: str) -> datetime:
                return datetime.strptime(birthday, "%Y-%m-%d")

        author = Author._construct(
            name="  first_name second_name  ",
            age=20,
            debut_year=2020,
            birthday="1998-01-01",
        )
        self.assertEqual("first_name second_name", author.name)
        self.assertEqual(21, author.age)
        self.assertEqual(2021, author.debut_year)
        self.assertEqual(datetime(1998, 1, 1), author.birthday)

        # test single dispatch method

        author = Author._construct(
            name="  first_name second_name  ",
            age=20,
            debut_year="2020",
            birthday=datetime(1998, 1, 1),
        )
        self.assertEqual(2020, author.debut_year)
        self.assertEqual(datetime(1998, 1, 2), author.birthday)

    def test_multiple_args(self):
        """
        Test that the method with multiple arguments is called correctly.
        :return:
        """

        @structured()
        @dataclasses.dataclass(frozen=True, kw_only=True)
        class Author:
            name: str
            age: int
            debut_year: int
            birthday: datetime

            @classmethod
            def clean_name(cls, first_name: str, second_name: str, **kwargs) -> str:
                return f"{first_name.strip()} {second_name.strip()}"

            @staticmethod
            def clean_age(age: int, **kwargs) -> int:
                return age + 1

            @singledispatchmethod
            @staticmethod
            def clean_debut_year(debut_year: int, **kwargs) -> int:
                return debut_year + 1

            @clean_debut_year.register
            @staticmethod
            def _(debut_year: str, **kwargs) -> int:
                return int(debut_year)

            @singledispatchmethod
            @classmethod
            def clean_birthday(cls, birthday: datetime, **kwargs) -> datetime:
                return birthday + timedelta(days=1)

            @clean_birthday.register
            @classmethod
            def _(cls, birthday: str, **kwargs) -> datetime:
                return datetime.strptime(birthday, "%Y-%m-%d")

        author = Author._construct(
            first_name="  first_name  ",
            second_name="  second_name  ",
            age=20,
            debut_year=2020,
            birthday="1998-01-01",
        )
        self.assertEqual("first_name second_name", author.name)
        self.assertEqual(21, author.age)
        self.assertEqual(2021, author.debut_year)
        self.assertEqual(datetime(1998, 1, 1), author.birthday)

    def test_auto_convert(self):
        """
        Test that the method var annotated as AutoConvert is converted correctly.
        :return:
        """

        @structured()
        @dataclasses.dataclass(frozen=True, kw_only=True)
        class Author:
            name: str

            @classmethod
            def clean_name(cls, name: str) -> str:
                assert isinstance(name, str)
                return name.strip()

        with self.assertRaises(AssertionError):
            Author._construct(name=123)

        @structured()
        @dataclasses.dataclass(frozen=True, kw_only=True)
        class Author:
            name: str

            @classmethod
            def clean_name(cls, name: Annotated[str, AutoConvert]) -> str:
                assert isinstance(name, str)
                return name.strip()

        author = Author._construct(name=123)
        self.assertEqual("123", author.name)
