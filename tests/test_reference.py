import dataclasses
from datetime import datetime
from unittest import TestCase

from fastructure import structured
from fastructure.reference import Reference


class TestReference(TestCase):
    def test_reference(self):
        @structured()
        @dataclasses.dataclass(frozen=True)
        class Author:
            name: str
            age: int
            debut_year: int
            init_var: dataclasses.InitVar[int] = dataclasses.field()
            birthday: datetime = datetime(2000, 1, 1)

            def __post_init__(self, init_var: int):
                assert isinstance(init_var, int)

            @classmethod
            def mapping(cls) -> dict:
                return {
                    "name": cls.name,
                    "age": cls.age,
                    "debut_year": cls.debut_year,
                    "birthday": cls.birthday,
                }

        self.assertIsInstance(Author.name, Reference)
        self.assertEqual(Author.name.path, "Author.name")

        self.assertIsInstance(Author.age, Reference)
        self.assertIsInstance(Author.debut_year, Reference)
        self.assertIsInstance(Author.birthday, Reference)

        author = Author._construct(name="John", age=20, debut_year=2020, init_var=20)
        self.assertEqual(datetime(2000, 1, 1), author.birthday)

        with self.assertRaises(AttributeError):
            Author.fuga

        self.assertDictEqual(
            {
                "name": Author.name,
                "age": Author.age,
                "debut_year": Author.debut_year,
                "birthday": Author.birthday,
            },
            Author.mapping(),
        )
