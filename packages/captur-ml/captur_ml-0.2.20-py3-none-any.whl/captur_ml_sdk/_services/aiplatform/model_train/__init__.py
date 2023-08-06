from google.cloud import aiplatform
from typing import Optional

from captur_ml_sdk.dtypes.exceptions import (
    GoogleCloudVertexAIDatasetDoesNotExistError,
    GoogleCloudVertexAIModelDoesNotExistError,
    GoogleCloudVertexAICompatibilityError
)
from google.api_core import exceptions as google_exceptions


def train_model(
    location: str,
    display_name: str,
    dataset_id: str,
    prediction_type: str,
    project: str = "capturpwa",
    model_type: str = "CLOUD",
    model_display_name: Optional[str] = None,
    multi_label: bool = False,
    base_model: Optional[str] = None,
    training_fraction_split: float = 0.8,
    validation_fraction_split: float = 0.1,
    test_fraction_split: float = 0.1,
    budget_milli_node_hours: int = 8000,
    disable_early_stopping: bool = False,
    sync: bool = True,
    create_request_timeout: float = 300
):

    aiplatform.init(project=project, location=location)

    try:
        if base_model:
            base_model = aiplatform.Model(base_model)
            if prediction_type == "classification" and base_model.predict_schemata.prediction_schema_uri != "'https://storage.googleapis.com/google-cloud-aiplatform/schema/predict/prediction/classification_1.0.0.yaml'":
                raise GoogleCloudVertexAICompatibilityError("Base model must be type classification. Object detecttion does not support the use of a base model.")
    except google_exceptions.NotFound:
        raise GoogleCloudVertexAIModelDoesNotExistError(f"Base model {base_model} not found.")

    if len(model_display_name) > 128:
        raise ValueError("job_display_name must be 128 characters or less.")

    if create_request_timeout > 300:
        raise ValueError("Request timeout must be 300 seconds or less.")

    job = aiplatform.AutoMLImageTrainingJob(
        display_name=display_name,
        base_model=base_model,
        prediction_type=prediction_type,
        multi_label=multi_label,
        model_type=model_type,
    )

    try:
        my_image_ds = aiplatform.ImageDataset(dataset_id)
    except google_exceptions.NotFound:
        raise GoogleCloudVertexAIDatasetDoesNotExistError(
            f"Dataset {dataset_id} does not exist"
        )

    try:
        model = job.run(
            dataset=my_image_ds,
            model_display_name=model_display_name,
            training_fraction_split=training_fraction_split,
            validation_fraction_split=validation_fraction_split,
            test_fraction_split=test_fraction_split,
            budget_milli_node_hours=budget_milli_node_hours,
            disable_early_stopping=disable_early_stopping,
            sync=sync,
            create_request_timeout=create_request_timeout
        )
    except (
        google_exceptions.InvalidArgument,
        google_exceptions.FailedPrecondition
    ) as e:
        if "The fraction values must sum to up to 1" in str(e):
            raise ValueError(
                f"Training fraction: {training_fraction_split}, validation fraction: {validation_fraction_split}, and test fraction: {test_fraction_split} do not sum to 1."
            )
        elif "The train budget milli node hours must be in the range [20000, 900000]" in str(e):
            model_type = str(e).split(" ")[-1]
            raise ValueError(
                f"Training budget milli node hours must be in the range [20000, 900000] for prediction type {prediction_type} and model type {model_type}."
            )
