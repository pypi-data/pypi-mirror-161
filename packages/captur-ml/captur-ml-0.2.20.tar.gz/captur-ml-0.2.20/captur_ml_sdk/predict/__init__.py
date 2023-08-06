from typing import Union, List

from captur_ml_sdk.dtypes import ImageClassificationResult
from captur_ml_sdk.dtypes.generics import Image
from captur_ml_sdk._services.aiplatform.live_predict import get_image_classification_prediction_from_deployed_automl


def get_live_automl_image_classification(
    endpoint_id: str,
    location: str,
    images: Union[Image, List[Image]],
    return_raw_automl_response: bool = False
):
    """Perform image classification on an image or list of images using AutoML.

    Args:
        endpoint_id (str): The VertexAI endpoint of the AutoML model that will perform the classification.
        location (str) : The location of the VertexAI endpoint.
        images (Union[Image, List[Image]]): The image(s) to classify.
        return_raw_automl_response (bool, optional): If True, AutoML response will not be cast to
            captur_ml_sdk.dtypes.ImageClassificationResult. Defaults to False.

    Returns:
        ImageClassificationResult: Result of the model prediction
    """
    if isinstance(images, Image):
        images = [images]

    image_classification_raw_results = [
        (
            image, get_image_classification_prediction_from_deployed_automl(
                endpoint_id=endpoint_id,
                location=location,
                image_data=image.data,
            )
        ) for image in images
    ]

    if return_raw_automl_response:
        return image_classification_raw_results

    image_classification_results = [
        ImageClassificationResult.from_automl_response(
            image, image_classification_raw_result
        ) for image, image_classification_raw_result in image_classification_raw_results
    ]

    return image_classification_results
