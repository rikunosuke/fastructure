from functools import cached_property
from typing import TYPE_CHECKING, Annotated, Any, Self, Type, get_args, get_origin

from fastructure.typehints import AutoConvert

if TYPE_CHECKING:
    from fastructure.base import BaseModel


class Annotation:
    def __init__(self, typehint: Any):
        self._typehint = typehint

    def __str__(self):
        return f"{self._typehint}"

    __repr__ = __str__

    @property
    def is_annotated(self) -> bool:
        return get_origin(self._typehint) is Annotated

    @property
    def has_auto_convert(self) -> bool:
        return any(anno.origin is AutoConvert for anno in self.children)

    @property
    def has_args(self) -> bool:
        return len(get_args(self._typehint)) > 0

    @cached_property
    def has_fastructure_model(self) -> bool:
        if self.is_fastructure_model:
            return True

        return any(ref.has_fastructure_model for ref in self.children)

    @cached_property
    def is_fastructure_model(self) -> bool:
        from fastructure.base import BaseModel

        try:
            return issubclass(self.origin, BaseModel)
        except TypeError:
            return False

    @cached_property
    def origin(self):
        if origin := get_origin(self._typehint):
            return origin
        return self._typehint

    @cached_property
    def children(self) -> list[Self]:
        if not self.has_args:
            return []

        return [
            Annotation(
                typehint=typehint,
            )
            for typehint in get_args(self._typehint)
        ]

    def get_child_annotation(self, index: int):
        if not self.has_args:
            raise ValueError(f"No annotation for {index}")

        if len(self.children) == 1:
            return self.children[0]

        return self.children[index]


class Reference(Annotation):
    def __init__(
        self,
        cls: Type["BaseModel"],
        cls_var_name: str,
        typehint: Any,
    ):
        self._cls = cls
        self._cls_var_name = cls_var_name
        super().__init__(typehint)

    @property
    def cls_var_name(self):
        return self._cls_var_name

    @property
    def is_ref(self) -> bool:
        return isinstance(self.origin, Reference)

    @cached_property
    def children(self) -> list[Self]:
        if not self.has_args:
            return []

        return [
            Reference(
                cls=self._cls,
                cls_var_name=self.cls_var_name,
                typehint=typehint,
            )
            for typehint in get_args(self._typehint)
        ]

    @property
    def path(self) -> str:
        return f"{self._cls.__name__}.{self.cls_var_name}"

    def __str__(self):
        return f"{self.__class__.__name__}({self.path})[{super().__str__()}]"

    __repr__ = __str__
