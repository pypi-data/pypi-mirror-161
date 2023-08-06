from google.cloud import aiplatform
from google.api_core import exceptions as google_exceptions
from captur_ml_sdk.dtypes.exceptions import (
    GoogleCloudVertexAIModelDoesNotExistError,
    GoogleCloudVertexAIResourceDoesNotExistError,
    GoogleCloudStorageBucketNotFoundError,
)
from captur_ml_sdk._services.storage import check_file_exists
from captur_ml_sdk.utils.file_formatting import (
    get_bucket_from_gs_uri, get_filepath_from_gs_uri
)

def make_batch_prediction(
    model_id: str,
    job_display_name: str,
    gcs_source: str,
    gcs_destination: str,
    project: str = "capturpwa",
    location: str = "us-central1",
    sync: bool = True,
):
    """Sends request to perform a batch prediction job.

    Args:
        model_id (str): GCP model id that uniquely identifies a machine learning model.
        job_display_name (str): the identifier that will appear in the batch prediction dashboard on GCP
        gcs_source (str): GCS filepath of the batch file. The batch file is a JSONL file that lists the image
            Google Storage URIs to be predicted.
        gcs_destination (str): GCS filepath to store outputted prediction JSON files.
        project (str, optional): The GCP project name. Defaults to "capturpwa".
        location (str, optional): The geographical location where the prediction service is performed. Should be
            the same location as the model specified by `model_id`. Defaults to "us-central1".
        sync (bool, optional): whether the batch prediction is performed synchronously or asynchronously. Defaults to True.

    Raises:
        GoogleCloudVertexAIModelDoesNotExistError: No model is found with id "model_id".
        GoogleCloudVertexAIBatchGCSSourceDoesNotExistError: Source batch file is not found.
        GoogleCloudStorageBucketNotFoundError: A Google Cloud Storage bucket is not found.
    """

    aiplatform.init(project=project, location=location)

    try:
        my_model = aiplatform.Model(model_id)
    except google_exceptions.NotFound:
        raise GoogleCloudVertexAIModelDoesNotExistError(f"Model {model_id} not found.")

    for error_detail, gcs_file in [("source", gcs_source), ("destination", gcs_destination)]:
        try:
            bucket = get_bucket_from_gs_uri(gcs_file)
            filepath = get_filepath_from_gs_uri(gcs_file)
            if not check_file_exists(bucket, filepath):
                raise GoogleCloudVertexAIResourceDoesNotExistError(f"GCS {error_detail} file '{gcs_file}' not found.")
        except GoogleCloudStorageBucketNotFoundError:
            raise GoogleCloudStorageBucketNotFoundError(f"GCS {error_detail} bucket '{gcs_file}' not found.")

    if len(job_display_name) > 128:
        raise ValueError("job_display_name must be 128 characters or less.")

    return my_model.batch_predict(
        job_display_name=job_display_name,
        gcs_source=gcs_source,
        gcs_destination_prefix=gcs_destination,
        sync=sync,
    )
