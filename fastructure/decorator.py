import dataclasses
from typing import Any, Callable, Type, Unpack

from fastructure.base import BaseModel
from fastructure.config import ConfigType
from fastructure.reference import Reference


def is_child(typehint: Any) -> bool:
    return issubclass(typehint, BaseModel) or isinstance(typehint, Reference)


def structured[
    T
](
    **kwargs: Unpack[ConfigType],
) -> Callable[
    [Type[dataclasses.dataclass]], Type[BaseModel]
]:
    def wrapper(dataclass_: T) -> Type[BaseModel]:
        if not dataclasses.is_dataclass(dataclass_):
            raise TypeError(f"{dataclass_} is not a dataclass.")

        if issubclass(dataclass_, BaseModel):
            cls = dataclass_
        else:
            cls = type(dataclass_.__name__, (dataclass_, BaseModel), {}, **kwargs)

        fields = dataclasses.fields(cls)
        cls._references = tuple(
            Reference(
                cls=cls,
                cls_var_name=field.name,
                typehint=field.type,
                is_child=is_child(field.type),
            )
            for field in fields
        )
        for ref in cls._references:
            setattr(cls, ref.cls_var_name, ref)

        return cls

    return wrapper
