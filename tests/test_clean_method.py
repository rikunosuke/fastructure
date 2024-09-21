import dataclasses
from datetime import datetime
from functools import singledispatchmethod
from unittest import TestCase

from fastructure import structured


@structured()
@dataclasses.dataclass(frozen=True)
class Author:
    first_name: str
    second_name: str
    birthday: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.second_name}"

    @classmethod
    def clean_first_name(cls, first_name: str) -> str:
        return first_name.strip()

    @classmethod
    def clean_second_name(cls, second_name: str) -> str:
        return second_name.strip()

    @singledispatchmethod
    @classmethod
    def clean_birthday(cls, birthday) -> datetime:
        raise NotImplementedError(f"Cannot clean {birthday}")

    @clean_birthday.register
    @classmethod
    def _(cls, birthday: str) -> datetime:
        return datetime.strptime(birthday, "%Y-%m-%d")

    @clean_birthday.register
    @classmethod
    def _(cls, birthday: datetime) -> datetime:
        return birthday

    @staticmethod
    def mapping() -> dict:
        json_mapping = {"name": Author.full_name, "birthday": Author.birthday}
        csv_mapping = {0: Author.full_name, 1: Author.birthday}
        return csv_mapping if True else json_mapping


class TestCleanMethod(TestCase):
    def test_clean_method(self):
        author = Author._construct(
            first_name="   John   ", second_name="   Doe   ", birthday="1990-01-01"
        )
        self.assertEqual("John", author.first_name)
        self.assertEqual("Doe", author.second_name)
        self.assertEqual(datetime(1990, 1, 1), author.birthday)

    def test_clean_method_with_singledispatch(self):
        author = Author._construct(
            first_name="John",
            second_name="Doe",
            birthday=datetime(1990, 1, 1),
        )
        self.assertEqual(datetime(1990, 1, 1), author.birthday)
