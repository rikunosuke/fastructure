from typing import Annotated, Any, get_args, get_origin


class Reference:
    def __init__(self, cls: str, cls_var_name: str, typehint: Any):
        self._cls = cls
        self._cls_var_name = cls_var_name
        self._typehint = typehint

    @property
    def cls_var_name(self):
        return self._cls_var_name

    @property
    def typehint(self):
        return self._typehint

    @property
    def to_type(self):
        if get_origin(self._typehint) is Annotated:
            return get_args(self._typehint)[0]
        return self._typehint

    @property
    def path(self) -> str:
        return f"{self._cls}.{self.cls_var_name}"

    def __str__(self):
        return f"{self.__class__.__name__} of ({self.path})"

    __repr__ = __str__
