import pydantic
from typing import List

from captur_ml_sdk.dtypes.generics import Image, Prediction
from google.cloud import aiplatform_v1


class ImageClassificationResult(pydantic.BaseModel):
    id: str = pydantic.Field(
        ...,
        description="The image used for the prediction.",
    )
    predictions: List[Prediction] = pydantic.Field(
        ...,
        description="The list of classification results for the image.",
    )

    @classmethod
    def from_automl_response(cls, image: Image, automl_response_object: aiplatform_v1.types.PredictResponse):
        # models_predictions will have one item for each model that has had predictions requested from it.
        #       In many situations it will therefore only have a single item.
        models_predictions = [dict(prediction) for prediction in automl_response_object.predictions]

        predictions = []
        for prediction in models_predictions:
            ids = prediction["ids"]
            class_names = prediction["displayNames"]
            confidences = prediction["confidences"]
            # ensure predictions are in descending order of confidence
            arr = [(conf, cls, id) for conf, cls, id in zip(confidences, class_names, ids)]
            arr.sort(reverse=True, key=lambda x: x[0])
            confidences = [x[0] for x in arr]
            class_names = [x[1] for x in arr]
            ids = [x[2] for x in arr]
            for id, name, confidence in zip(ids, class_names, confidences):
                pred = Prediction(id=id, displayName=name, confidence=confidence)
                predictions.append(pred)

        return cls(id=image.id, predictions=predictions)
