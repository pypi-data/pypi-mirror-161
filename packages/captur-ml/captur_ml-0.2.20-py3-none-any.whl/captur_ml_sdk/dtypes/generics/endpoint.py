import pydantic

from typing import Optional

class Endpoint(pydantic.BaseModel):
    id: str = pydantic.Field(
        ...,
        description='A unique identifier for the VertexAI Endpoint.'
    )
    location: str = pydantic.Field(
        ...,
        description='The global location of the VertexAI Endpoint.'
    )
