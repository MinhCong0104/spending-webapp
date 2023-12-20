from typing import Annotated, Any, Callable

from pydantic_core import core_schema
from app.infra.database.models.category import Category


class _PydanticCategoryType(Category):
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: Callable[[Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        return core_schema.union_schema(
            [
                # check if it's an instance first before doing any further work
                core_schema.is_instance_schema(Category),
                core_schema.no_info_plain_validator_function(cls.validate),
            ],
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, value: Category) -> Category:
        return value.validate()


PydanticCategoryType = Annotated[Category, _PydanticCategoryType]
