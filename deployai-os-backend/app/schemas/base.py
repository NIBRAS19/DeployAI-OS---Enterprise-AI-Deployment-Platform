from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base for every schema: Python fields stay snake_case, but JSON in and
    out uses camelCase — matching the interfaces already defined in the
    frontend's lib/types.ts with no translation layer on either side.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
