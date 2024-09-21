import inspect
from functools import cached_property
from typing import Any, Callable, get_args

from fastructure.config import Config
from fastructure.exceptions import InvalidParameterName


class ParameterParser[**P]:

    def __init__(
        self,
        method: Callable,
        config: Config,
        params: P.kwargs,
    ):
        self._config = config
        self._method = method
        self._parameters = inspect.signature(method).parameters
        self._params = params

    @property
    def _is_single_dispatch(self) -> bool:
        return hasattr(self._method, "register")

    @property
    def _field_name(self) -> str:
        return self._config.substring_field_name(self._method.__name__)

    def _sub_kwargs(self, **kwargs: P.kwargs) -> tuple[list, dict]:
        # if method has **kwargs, return all kwargs
        if any(p.kind == p.VAR_KEYWORD for p in self._parameters.values()):
            if self._is_single_dispatch:
                # singledispatchmethod required only one parameter
                return [kwargs[self._field_name]], {
                    k: v for k, v in kwargs.items() if k != self._field_name
                }
            return [], kwargs

        param_names = [
            k
            for k, p in self._parameters.items()
            if p.kind != p.VAR_KEYWORD and p.kind != p.VAR_POSITIONAL
        ]
        pos_only = [
            k for k, p in self._parameters.items() if p.kind == p.POSITIONAL_ONLY
        ]
        # if method has cls, remove it from param_names
        if isinstance(self._method, classmethod) or self._is_single_dispatch:
            # it's impossible to check if method is classmethod or staticmethod wrapped
            # by singledispatchmethod, so we check if method has "register" attribute
            # and remove "cls" from param_names
            if param_names[0] in self._config.class_itself_var_names:
                param_names = param_names[1:]
        if self._is_single_dispatch and not pos_only:
            # singledispatchmethod required at least one positional argument
            pos_only = [param_names[0]]
        param_names = [p for p in param_names if p in kwargs]
        try:
            return [kwargs[p] for p in param_names if p in pos_only], {
                p: kwargs[p] for p in param_names if p not in pos_only
            }
        except KeyError as e:
            raise InvalidParameterName(
                f"Method '{self._method.__name__}' has no parameter named: "
                f"{str(e).replace("KeyError: ", "")}"
            )

    @property
    def list_params(self) -> list:
        return self._parsed[0]

    @property
    def dict_params(self) -> dict:
        return self._parsed[1]

    @cached_property
    def _parsed(self) -> tuple[list, dict]:
        params = {k: self._convert(k, v) for k, v in self._params.items()}
        return self._sub_kwargs(**params)

    def _convert(self, field_name: str, value: Any) -> Any:
        try:
            annotation = self._parameters[field_name].annotation
        except KeyError:
            return value

        if not self._config.is_convertible(annotation):
            return value
        try:
            base_cls = get_args(annotation)[0]
        except IndexError:
            base_cls = annotation
        converter = self._config.converter_class(value=value, to_type=base_cls)
        return converter.execute()
