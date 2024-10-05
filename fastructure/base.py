import inspect
from typing import ClassVar, Type, Unpack, Any

from fastructure.config import Config, ConfigType, MapType
from fastructure.converters import Converter
from fastructure.exceptions import ConvertError as BaseConvertError
from fastructure.exceptions import ValidationError as BaseValidationError
from fastructure.parameter_parser import ParameterParser
from fastructure.reference import Reference


class BaseModel:
    _config: ClassVar[Config]
    _references: ClassVar[tuple[Reference]]

    def __init_subclass__(
        cls, *, converter: Type[Converter] = Converter, **kwargs: Unpack[ConfigType]
    ):
        cls._config = Config(converter=converter, **kwargs)

    class ValidationError(BaseValidationError):
        """Raised when a value does not pass validation."""

        pass

    class ConvertError(BaseConvertError):
        """Raised when a value cannot be converted to the correct type."""

        pass

    @classmethod
    def clean(cls, **kwargs) -> dict:
        return kwargs

    @classmethod
    def _construct(cls, **kwargs) -> "BaseModel":
        original_values = cls._add_keys(kwargs.copy())
        for field_name, original_val in original_values.items():
            try:
                clean_method = cls._config.get_clean_method(field_name, cls)
            except AttributeError:
                try:
                    ref = [
                        ref for ref in cls._references if ref.cls_var_name == field_name
                    ][0]
                except IndexError:
                    continue

                kwargs[ref.cls_var_name] = cls._config.parse(
                    value=original_val, annotation=ref
                )
                continue

            if not callable(clean_method):
                continue

            parser = ParameterParser(clean_method, cls._config, original_values.copy())
            kwargs[field_name] = clean_method(*parser.list_params, **parser.dict_params)

        parser_for_clean = ParameterParser(cls.clean, cls._config, kwargs.copy())
        cleaned = kwargs | cls.clean(
            *parser_for_clean.list_params, **parser_for_clean.dict_params
        )
        init_parser = ParameterParser(cls, cls._config, cleaned)
        return cls(*init_parser.list_params, **init_parser.dict_params)

    @classmethod
    def _add_keys(cls, data: dict) -> dict:
        """
        insert clean method keys to data.
        """
        for method_name, _ in inspect.getmembers(cls, predicate=inspect.ismethod):
            # set clean method to None if it's not in kwargs
            try:
                field_name = cls._config.substring_field_name(method_name)
            except ValueError:
                continue

            if field_name not in data:
                data[field_name] = None

        return data

    @classmethod
    def dict_map(cls) -> dict[str, MapType]:
        return {ref.cls_var_name: ref for ref in cls._references}

    @classmethod
    def list_map(cls) -> dict[int, MapType] | list[MapType]:
        return {i: ref for i, ref in enumerate(cls._references)}

    @classmethod
    def from_dict(cls, data: dict) -> "BaseModel":
        dict_map = cls._config.get_dict_map(cls)
        kwargs = {}
        for expected_key, ref in dict_map.items():
            if expected_key not in data:
                raise cls.ValidationError(f"{expected_key} is required.")

            var_name = ref.cls_var_name if isinstance(ref, Reference) else ref
            kwargs[var_name] = data[expected_key]

        return cls._construct(**kwargs)

    @classmethod
    def from_list(cls, data: list) -> "BaseModel":
        list_map = cls._config.get_list_map(cls)
        list_result = (
            list_map
            if isinstance(list_map, dict)
            else {i: value for i, value in enumerate(list_map)}
        )
        kwargs = {}
        for i, ref in list_result.items():
            if i >= len(data):
                raise cls.ValidationError(
                    f"class '{cls.__name__}' must have a list map with length {len(data)}"
                )

            var_name = ref.cls_var_name if isinstance(ref, Reference) else ref
            kwargs[var_name] = data[i]
        return cls._construct(**kwargs)

    @classmethod
    def construct(cls, **kwargs) -> "BaseModel":
        return cls._construct(**kwargs)
