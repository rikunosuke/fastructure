from typing import TYPE_CHECKING, Annotated, Any, Callable, Type, TypedDict, get_origin

from fastructure.converters import Converter
from fastructure.reference import Reference, Annotation
from fastructure.typehints import AutoConvert

if TYPE_CHECKING:
    from fastructure.base import BaseModel

CLEAN_METHOD_PREFIX = "clean_"
DICT_MAP_METHOD_NAME = "dict_map"
LIST_MAP_METHOD_NAME = "list_map"


type MapType = str | Reference | "BaseModel"


class ConfigType(TypedDict, total=False):
    clean_method_prefix: str
    converter: Type[Converter]
    convert_all: bool
    mapping_method: str
    class_itself_var_names: list[str] | None


class Config:
    def __init__(
        self,
        *,
        converter: Type[Converter],
        convert_all: bool = False,
        dict_map_method: str = DICT_MAP_METHOD_NAME,
        list_map_method: str = LIST_MAP_METHOD_NAME,
        clean_method_prefix: str = CLEAN_METHOD_PREFIX,
        class_itself_var_names: list[str] | None = None,
    ):
        self.clean_method_prefix = clean_method_prefix
        self.convert_all = convert_all
        self._converter_class = converter
        self.dict_map_method = dict_map_method
        self.list_map_method = list_map_method
        self.class_itself_var_names = ["cls"] + (class_itself_var_names or [])

    def _get_clean_method_name(self, field_name: str) -> str:
        return f"{self.clean_method_prefix}{field_name}"

    def get_clean_method(self, field_name: str, model: Type["BaseModel"]) -> Callable:
        method_name = self._get_clean_method_name(field_name)
        return getattr(model, method_name)

    def substring_field_name(self, method_name: str) -> str:
        if not method_name.startswith(self.clean_method_prefix):
            raise ValueError(
                f"Method {method_name} does not start with {self.clean_method_prefix}"
            )
        return method_name.replace(self.clean_method_prefix, "")

    def get_dict_map(self, model: Type["BaseModel"]) -> dict[str, MapType]:
        try:
            return getattr(model, self.dict_map_method)()
        except AttributeError as e:
            e.add_note(f"Model {model} has no method `{self.dict_map_method}`")
            raise

    def get_list_map(
        self, model: Type["BaseModel"]
    ) -> dict[int, MapType] | list[MapType]:
        try:
            return getattr(model, self.list_map_method)()
        except AttributeError as e:
            e.add_note(f"Model {model} has no method `{self.list_map_method}`")
            raise

    def _is_convertible(self, annotation: Annotation) -> bool:
        if self.convert_all:
            return True

        if annotation.origin is not Annotated:
            return False

        return annotation.has_auto_convert

    def parse(self, value, annotation: Annotation):
        if not self._is_convertible(annotation):
            return value

        return self._recursive_parse(value, annotation)

    def _recursive_parse(self, value, annotation: Annotation):
        """
        expected typehint:
            var: Annotated[int, ...]
            var: list[int]
            var: list[int, str]
            var: int
            var: BaseModel
            var: list[BaseModel]
        """
        if annotation.is_annotated:
            return self._recursive_parse(value, annotation.get_child_annotation(0))
        if annotation.has_args:
            return value.__class__(
                self._recursive_parse(val, annotation.get_child_annotation(i))
                for i, val in enumerate(value)
            )

        return self._converter_class(value, annotation.origin).execute()
