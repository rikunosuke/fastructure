import dataclasses
from typing import Callable, Type, Unpack

from fastructure.base import BaseModel
from fastructure.config import ConfigType
from fastructure.reference import Reference


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
                cls=cls.__name__,
                cls_var_name=field.name,
                typehint=field.type,
            )
            for field in fields
        )
        for ref in cls._references:
            setattr(cls, ref.cls_var_name, ref)

        return cls

    return wrapper
