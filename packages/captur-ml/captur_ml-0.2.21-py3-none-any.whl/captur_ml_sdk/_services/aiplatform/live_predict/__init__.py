import re
from captur_ml_sdk.dtypes.exceptions import (
    GoogleCloudVertexAIEndpointDoesNotExistError,
    GoogleCloudVertexAIEndpointImageTooLargeError,
    GoogleCloudVertexAIEndpointNoModelDeployedError,
)

from google.cloud import aiplatform_v1
from google.cloud.aiplatform.gapic import PredictionServiceClient, schema
from google.api_core import exceptions as google_exceptions


def get_image_classification_prediction_from_deployed_automl(
    image_data: str,
    endpoint_id: str,
    project: str = "capturpwa",
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
) -> aiplatform_v1.types.PredictResponse:
    """Gets image classification prediction from deployed automl model.

    Args:
        image_data (str): utf-8 encoded string of image.
        endpoint_id (str): The id that uniquely identifies the GCP Vertex AI endpoint at which the model is deployed.
        project (str, optional): The GCP project name. Defaults to "capturpwa".
        location (str, optional): The global location where the prediction computation takes place. Defaults to "us-central1".
        api_endpoint (str, optional): The endpoint provided by the client. Defaults to "us-central1-aiplatform.googleapis.com".

    Raises:
        GoogleCloudVertexAIEndpointDoesNotExistError: The specified endpoint does not exist.
        GoogleCloudVertexAIEndpointNoModelDeployedError: There is no model deployed at the specified endpoint.
        GoogleCloudVertexAIEndpointImageTooLargeError: The image exceeds the 1.5MB limit.

    Returns:
        automl_v1beta1.types.PredictResponse: An object containing the prediction results for the image.
    """
    client_options = {"api_endpoint": api_endpoint}
    client = PredictionServiceClient(client_options=client_options)

    instance = schema.predict.instance.ImageClassificationPredictionInstance(
        content=image_data,
    ).to_value()
    instances = [instance]

    parameters = schema.predict.params.ImageClassificationPredictionParams(
        confidence_threshold=0.0, max_predictions=10,
    ).to_value()

    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    try:
        response = client.predict(
            endpoint=endpoint, instances=instances, parameters=parameters
        )
    except google_exceptions.NotFound:
        raise GoogleCloudVertexAIEndpointDoesNotExistError(f"Endpoint {endpoint_id} not found.")

    except google_exceptions.FailedPrecondition as e:
        if "doesn't have traffic_split" in str(e):
            raise GoogleCloudVertexAIEndpointNoModelDeployedError(f"No model is deployed at endpoint {endpoint_id}.")
        elif re.search(r"exceeds \d*.* limit", str(e)) is not None:
            match = re.search(r"exceeds (\d*.*) limit", str(e))
            size_limit = match.group(1)
            raise GoogleCloudVertexAIEndpointImageTooLargeError(size_limit)

    return response
