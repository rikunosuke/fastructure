from typing import TYPE_CHECKING, Annotated, Any, Type, get_args, get_origin

if TYPE_CHECKING:
    from fastructure.base import BaseModel


class Reference:
    def __init__(
        self,
        cls: Type["BaseModel"],
        cls_var_name: str,
        typehint: Any,
        is_child: bool,
    ):
        self._cls = cls
        self._cls_var_name = cls_var_name
        self._typehint = typehint
        self._is_child = is_child

    @property
    def cls_var_name(self):
        return self._cls_var_name

    @property
    def typehint(self):
        return self._typehint

    @property
    def is_child(self) -> bool:
        return self._is_child

    @property
    def child_cls(self) -> Type["BaseModel"]:
        if not self.is_child:
            raise ValueError("Not a child.")

        return self.to_type

    @property
    def to_type(self):
        if get_origin(self._typehint) is Annotated:
            return get_args(self._typehint)[0]
        return self._typehint

    @property
    def path(self) -> str:
        return f"{self._cls.__name__}.{self.cls_var_name}"

    def __str__(self):
        return f"{self.__class__.__name__} of ({self.path})"

    __repr__ = __str__
