from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, ConfigDict, model_validator

SortType = Literal["asc", "desc"]
# FilterType = Literal["ge", "gt","le","lt","e","like","ilike"]


T = TypeVar('T', bool, str, int, float)


class FilterType(BaseModel, Generic[T]):
    and_: Optional[Literal[1, 0]] = None
    ge: Optional[T] = None
    gt: Optional[T] = None
    le: Optional[T] = None
    lt: Optional[T] = None
    e: Optional[T] = None
    like: Optional[T] = None
    ilike: Optional[T] = None

    model_config = ConfigDict(extra='forbid')

    @model_validator(mode="before")
    def validate_filters(cls, values):
        if values.get("and_", None) is None:
            if len(values) > 1:
                raise ValueError("Поле 'and_' должно быть указано, если присутствует более одного фильтра.")

        elif len(values) == 2:
            raise ValueError("Поле 'and_' должно быть пустым, если присутствует ровно один фильтр.")
        return values


class SortedData_Schema(BaseModel):
    __SORTING_RULES: Dict[str, SortType] = None

    sorting_order: Union[str, List[str]] = None

    @classmethod
    def validate_sorting_order(cls, v):
        if isinstance(v, str):
            return v.split(',')
        return v

    @model_validator(mode="before")
    def populate_data(cls, values):
        sorting_order = values.get("sorting_order", None)
        sorting_order = cls.validate_sorting_order(sorting_order)

        data = {}
        for key, value in values.items():
            if isinstance(value, str) and value.strip().lower() in {"asc", "desc"}:
                new_key = key.split("s__")
                if len(new_key) == 2:
                    data[new_key[1]] = value.strip().lower()

        if sorting_order:
            sorted_data = {}
            for key in sorting_order:
                if key in data:
                    sorted_data[key] = data[key]
            for key in data:
                if key not in sorted_data:
                    sorted_data[key] = data[key]
            cls.__SORTING_RULES = sorted_data

        else:
            cls.__SORTING_RULES = data

        return values

    def get_fill_data_sorting_order(self) -> Dict[str, Literal["asc", "desc"]]:
        return self.__SORTING_RULES


class FilteredData_Schema(BaseModel):
    __FILTER_RULES: Dict[str, Dict[FilterType, Any]] = None

    @model_validator(mode="before")
    def populate_filters(cls, values):
        filters = {}
        for key, value in values.items():
            if isinstance(value, dict):
                for local_key, local_value in value.items():
                    if local_key in FilterType.__fields__:
                        new_key = key.split("f__")
                        if len(new_key) == 2:
                            filters[new_key[1]] = value

        cls.__FILTER_RULES = filters
        return values

    def get_filter_rules(self) -> Dict[str, Any]:
        return self.__FILTER_RULES
