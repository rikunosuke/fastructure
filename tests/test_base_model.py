import dataclasses
from unittest import TestCase

from fastructure import structured


class TestInitSubclass(TestCase):
    def test_clean_method_prefix(self):

        @structured(clean_method_prefix="fix_")
        @dataclasses.dataclass(frozen=True)
        class Author:
            name: str

            @classmethod
            def fix_name(cls, name: str) -> str:
                return name.strip()

        author = Author._construct(name="   John   ")
        self.assertEqual("John", author.name)
