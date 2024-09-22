# Fastructure

Fastructure is a Python package designed to facilitate structured data handling and conversion.
It provides utilities for mapping, cleaning, and converting data between different formats such as dictionaries and lists.

## Features

- **Data Mapping**: Easily map data fields between different formats.
- **Data Cleaning**: Define custom cleaning methods for data fields.
- **Data Conversion**: Automatically convert data types based on annotations.

## Installation

To install Fastructure, use pip:

```sh
pip install fastructure
```

## Usage

### Defining a Model

You can define a model using the `@structured` decorator and `dataclasses.dataclass`:

```python
import dataclasses
from datetime import datetime
from fastructure import structured

@structured(convert_all=True)
@dataclasses.dataclass(frozen=True)
class Author:
    name: str
    age: int
    birthday: datetime
```

### Mapping Data

You can map data from dictionaries or lists to your model:

```python
# default
author = Author.construct(name="John", age=20, birthday="2000-01-01")

# from_dict
author = Author.from_dict({"name": "John", "age": 20, "birthday": "2000-01-01"})
print(author)

# from_list
author = Author.from_list(["John", 20, "2000-01-01"])
print(author)
```

```python
# custom

@structured(convert_all=True)
@dataclasses.dataclass(frozen=True)
class Author:
    name: str
    age: int
    birthday: datetime
    
    @classmethod
    def clean_name(cls, first_name: str, second_name: str) -> str:
        return f"{first_name} {second_name}"

    @classmethod
    def dict_map(cls) -> dict:
        return {
            "first-name": "first_name",
            "second-name": "second_name",
            "my-age": cls.age,
            "my-birthday": cls.birthday,
        }
    
    @classmethod
    def list_map(cls) -> dict:
        return {
            0: "first-name",
            1: "second-name",
            2: cls.age,
            3: cls.birthday,
        }

author = Author.from_dict({
    "first-name": "John",
    "second-name": "Doe",
    "my-age": 20,
    "my-birthday": "2000-01-01"
})
author = Author.from_list(["John", "Doe", 20, "2000-01-01"])
```

### Cleaning Data

Define custom cleaning methods for your model fields:

```python
@structured(convert_all=True)
@dataclasses.dataclass(frozen=True)
class Person:
    name: str
    age: int
    birthday: datetime

    @classmethod
    def clean_name(cls, name: str) -> str:
        return name.strip()
```

## Data Conversion

Fastructure provides utilities to automatically convert data types based on annotations. This feature is particularly useful when you need to ensure that data conforms to specific types.

### Defining a Model with Conversion

You can define a model using the `@structured` decorator and `dataclasses.dataclass`. Use the `convert_all` parameter to enable or disable automatic conversion for all fields.
You can also use the `Annotated` type hint with `AutoConvert` to specify fields that should be automatically converted.

```python
import dataclasses
from datetime import datetime
from typing import Annotated
from fastructure import structured
from fastructure.typehints import AutoConvert

@structured(convert_all=False)
@dataclasses.dataclass(frozen=True)
class Author:
    name: str
    age: int
    birthday: Annotated[datetime, AutoConvert]

    @classmethod
    def clean_age(cls, age: int, birthday: Annotated[datetime, AutoConvert]) -> int:
        # argument birthday is automatically converted to datetime
        assert datetime.now().year - birthday.year >= age, "Invalid age"
        return age

author = Author.construct(name="John", age=20, birthday="2000-01-01")
```

In this example, only the `birthday` field will be automatically converted to a `datetime` object.

```python
@structured(convert_all=True)
@dataclasses.dataclass(frozen=True)
class Author:
    name: str
    age: int
    birthday: datetime

author = Author.construct(name="John", age="20", birthday="2000-01-01")
```

In this example, all fields will be automatically converted to the correct data type.

## License

This project is licensed under the MIT License.
