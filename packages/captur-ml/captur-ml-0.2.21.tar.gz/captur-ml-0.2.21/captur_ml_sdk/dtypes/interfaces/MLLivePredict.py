import pydantic

from captur_ml_sdk.dtypes import ImageClassificationResult
from captur_ml_sdk.dtypes.generics import Endpoint
from typing import List


class LivePredictionRequest(pydantic.BaseModel):
    endpoint: Endpoint = pydantic.Field(
        ...,
        description="The ID and location of the VertexAI endpoint to use for prediction.",
    )
    image_url: pydantic.AnyUrl = pydantic.Field(
        ...,
        description="The URL of the image to use for prediction.",
    )
    webhooks: List[pydantic.AnyUrl] = pydantic.Field(
        ...,
        description="List of webhooks to which the prediction results will be sent.",
    )

class LivePredictionResponse(pydantic.BaseModel):
    endpoint: Endpoint = pydantic.Field(
        ...,
        description="The ID and location of the VertexAI endpoint to use for prediction.",
    )
    images: List[ImageClassificationResult] = pydantic.Field(
        ...,
        description='The list of classification results of the images used for the prediction.'
    )
