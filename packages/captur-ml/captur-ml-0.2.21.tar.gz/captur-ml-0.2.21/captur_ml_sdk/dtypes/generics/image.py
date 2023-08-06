import pydantic

from typing import Optional

class Image(pydantic.BaseModel):
    id: str = pydantic.Field(
        "",
        description='A unique identifier of the image'
    )
    url: Optional[pydantic.AnyUrl] = pydantic.Field(
        "",
        description='An http[s]:// or gs:// URL pointing to the image resource. Required if `data` is not specified.'
    )
    data: Optional[str] = pydantic.Field(
        "",
        description='The image bytes encoded as a UTF-8 string. Required if `url` is not specified.'
    )

    @pydantic.root_validator
    def must_contain_url_or_data(cls, values):
        if not values.get("url") and not values.get("data"):
            raise ValueError("Either `url` or `data` must be specified.")
        return values
