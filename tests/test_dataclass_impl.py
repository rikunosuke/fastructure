import dataclasses
from datetime import datetime
from typing import Annotated
from unittest import TestCase

from fastructure import structured
from fastructure.typehints import AutoConvert


class TestInitVar(TestCase):
    def test_init_var_convert_all(self):
        @structured(convert_all=True)
        @dataclasses.dataclass()
        class Author:
            name: str
            age: int
            init_var: dataclasses.InitVar[int]
            birthday: datetime = dataclasses.field(init=False)

            def __post_init__(self, init_var: int):
                assert isinstance(init_var, int)
                self.birthday = datetime.fromtimestamp(init_var)

            @classmethod
            def mapping(cls) -> dict:
                return {
                    "name": cls.name,
                    "age": cls.age,
                    "birthday": cls.birthday,
                }

        author = Author._construct(name="John Doe", age=10, init_var="1000000000")
        self.assertEqual("John Doe", author.name)
        self.assertEqual(10, author.age)
        self.assertEqual(datetime.fromtimestamp(1000000000), author.birthday)

    def test_init_var_manual_convert(self):
        @structured()
        @dataclasses.dataclass()
        class Author:
            name: str
            age: int
            init_var: dataclasses.InitVar[Annotated[int, AutoConvert]]
            birthday: datetime = dataclasses.field(init=False)

            def __post_init__(self, init_var: int):
                self.birthday = datetime.fromtimestamp(init_var)

            @classmethod
            def mapping(cls) -> dict:
                return {
                    "name": cls.name,
                    "age": cls.age,
                    "birthday": cls.birthday,
                }

        author = Author._construct(name="John Doe", age=10, init_var="1000000000")
        self.assertEqual("John Doe", author.name)
        self.assertEqual(10, author.age)
        self.assertEqual(datetime.fromtimestamp(1000000000), author.birthday)
