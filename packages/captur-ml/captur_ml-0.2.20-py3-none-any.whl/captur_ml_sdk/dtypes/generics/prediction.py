import pydantic

class Prediction(pydantic.BaseModel):
    id: str = pydantic.Field(
        "",
        description='A unique identifier of the Prediction'
    )
    displayName: str = pydantic.Field(
        ...,
        description='A human-readable name of the Prediction'
    )
    confidence: float = pydantic.Field(
        ...,
        description='The statistical confidence of the Prediction'
    )
