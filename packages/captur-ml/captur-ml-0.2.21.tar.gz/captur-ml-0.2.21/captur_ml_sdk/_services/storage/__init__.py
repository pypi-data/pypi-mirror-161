import json
from typing import Any, Dict, List, Union, Literal, Optional

from google.cloud import storage
from google.auth import exceptions as ga_exceptions
from google.api_core import exceptions as google_exceptions

from captur_ml_sdk.dtypes.exceptions import (
    GoogleCloudStoragePermissionError,
    GoogleCloudStorageResourceNotFoundError,
    GoogleCloudStorageBucketNotFoundError,
)


def _get_storage_client() -> storage.Client:
    """Wrapper function that returns an instance of the Google Cloud Storage client with added Exception handling.

    Raises:
        GoogleCloudStoragePermissionError: If the user does not have permission to access the Google Cloud Storage bucket, for example if there is
            no credentials file or the credentials file is invalid.

    Returns:
        storage.Client: A Google Cloud Storage client instance.
    """
    try:
        storage_client = storage.Client()
    except ga_exceptions.DefaultCredentialsError:
        raise GoogleCloudStoragePermissionError("Failed to create Google Cloud Storage client. Google Cloud Storage permissions are not configured.")

    return storage_client


def write_file_to_gcs(file_contents: Union[str, bytes], bucket_name: str, destination_filename: str, storage_client: Optional[storage.Client] = None):
    """Writes a file of either string or bytes content type to Google Cloud Storage.

    Args:
        file_contents (Union[str, bytes]): The contents of the file to write to Google Cloud Storage.
        bucket_name (str): The name of the Google Cloud Storage bucket to write the file to.
        destination_filename (str): The name of the file to write to Google Cloud Storage.
        storage_client (Optional[storage.Client], optional): A Google Cloud Storage client instance. If not provided, a new instance will be created. Defaults to None.

    Raises:
        GoogleCloudStorageResourceNotFoundError: If the Google Cloud Storage bucket does not exist.
    """
    if storage_client is None:
        storage_client = _get_storage_client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_filename)

    try:
        blob.upload_from_string(file_contents)
    except google_exceptions.NotFound:
        raise GoogleCloudStorageResourceNotFoundError(f"Failed to write file to Google Cloud Storage. Bucket {bucket_name} not found.")


def write_json_to_gcs(json_dict: Dict[Any, Any], bucket_name: str, destination_filename: str, storage_client: Optional[storage.Client] = None):
    """Writes a JSON file to Google Cloud Storage.

    Args:
        json_dict (Dict[Any, Any]): The dictionary to export as JSON to Google Cloud Storage.
        bucket_name (str): The name of the Google Cloud Storage bucket to write the file to.
        destination_filename (str): The name of the file to write to Google Cloud Storage. If it does not end with the .json extension, it will be added.
        storage_client (Optional[storage.Client], optional): A Google Cloud Storage client instance. If not provided, a new instance will be created. Defaults to None.

    Raises:
        ValueError: If the dictionary cannot be serialized to JSON.
    """
    if not destination_filename.endswith(".json"):
        destination_filename = f"{destination_filename}.json"

    try:
        json_string = json.dumps(json_dict)
        json.loads(json_string)
    except json.JSONDecodeError:
        raise ValueError("Failed to write JSON to Google Cloud Storage. JSON data is not valid.")

    write_file_to_gcs(json_string, bucket_name=bucket_name, destination_filename=destination_filename, storage_client=storage_client)


def write_jsonl_to_gcs(json_lines: List[Dict], bucket_name: str, destination_filename: str, storage_client: Optional[storage.Client] = None):
    """Writes a JSON file to Google Cloud Storage.

    Args:
        json_lines (List[Dict]): List of dictionaries to export as JSON lines to Google Cloud Storage.
        bucket_name (str): The name of the Google Cloud Storage bucket to write the file to.
        destination_filename (str): The name of the file to write to Google Cloud Storage. If it does not end with the .json extension, it will be added.
        storage_client (Optional[storage.Client], optional): A Google Cloud Storage client instance. If not provided, a new instance will be created. Defaults to None.

    Raises:
        ValueError: If the dictionary cannot be serialized to JSON.
    """
    if not destination_filename.endswith(".jsonl"):
        destination_filename = f"{destination_filename}.jsonl"

    try:
        json_lines_string = ""
        for line in json_lines:
            json_lines_string += json.dumps(line) + "\n"
    except json.JSONDecodeError:
        raise ValueError("Failed to write JSON to Google Cloud Storage. JSON data is not valid.")

    write_file_to_gcs(json_lines_string, bucket_name=bucket_name, destination_filename=destination_filename, storage_client=storage_client)


def read_file_from_gcs(bucket_name: str, origin_filename: str, read_mode: Literal["r", "b"] = "r", storage_client: Optional[storage.Client] = None) -> Union[bytes, str]:
    """Reads a file from Google Cloud Storage.

    Args:
        bucket_name (str): The name of the Google Cloud Storage bucket to read the file from.
        origin_filename (str): The name of the file to read from Google Cloud Storage.
        read_mode (Literal["r", "b"], optional): The mode to read the file in. "r" for text, "b" for bytes. Defaults to "r".
        storage_client (Optional[storage.Client], optional): A Google Cloud Storage client instance. If not provided, a new instance will be created. Defaults to None.

    Raises:
        GoogleCloudStorageResourceNotFoundError: If the Google Cloud Storage bucket or file does not exist.
        ValueError: If the read_mode is not "b" but the file cannot be decoded as UTF-8.

    Returns:
        Union[bytes, str]: The raw contents of the file.
    """
    if storage_client is None:
        storage_client = _get_storage_client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(origin_filename)

    try:
        contents = blob.download_as_bytes()
    except google_exceptions.NotFound:
        raise GoogleCloudStorageResourceNotFoundError(f"Failed to read file from Google Cloud Storage. File {bucket_name}/{origin_filename} not found.")

    if read_mode != "b" and type(contents) is bytes:
        try:
            contents = contents.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(f"Failed to decode file-bytes from Google Cloud Storage. File {bucket_name}/{origin_filename} is not a valid UTF-8 string. Please use read_mode='b' to read bytes.")

    return contents


def delete_file_from_gcs(bucket_name: str, destination_filename: str, storage_client: Optional[storage.Client] = None):
    """Deletes a file from Google Cloud Storage.

    Args:
        bucket_name (str): The name of the Google Cloud Storage bucket to delete the file from.
        destination_filename (str): The name of the file to delete from Google Cloud Storage.
        storage_client (Optional[storage.Client], optional): A Google Cloud Storage client instance. If not provided, a new instance will be created. Defaults to None.

    Raises:
        GoogleCloudStorageResourceNotFoundError: If the Google Cloud Storage bucket or file does not exist.
    """
    if storage_client is None:
        storage_client = _get_storage_client()

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_filename)

    try:
        blob.delete()
    except google_exceptions.NotFound:
        raise GoogleCloudStorageResourceNotFoundError(f"Failed to delete file from Google Cloud Storage. File {bucket_name}/{destination_filename} not found.")


def check_bucket_exists(bucket_name: str, storage_client: Optional[storage.Client] = None) -> bool:
    """Checks if a Google Cloud Storage bucket exists.

    Args:
        bucket_name (str): The name of the Google Cloud Storage bucket to check.
        storage_client (Optional[storage.Client], optional): A Google Cloud Storage client instance. If not provided, a new instance will be created. Defaults to None.

    Returns:
        bool: True if the bucket exists, False otherwise.
    """
    if storage_client is None:
        storage_client = _get_storage_client()

    bucket = storage_client.bucket(bucket_name)
    return bucket.exists()


def check_file_exists(bucket_name: str, file_name: str, storage_client: Optional[storage.Client] = None) -> bool:
    """Checks if a file exists in Google Cloud Storage.

    Args:
        gcs_filename (str): The name of the file to check.
        storage_client (Optional[storage.Client], optional): A Google Cloud Storage client instance. If not provided, a new instance will be created. Defaults to None.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    if storage_client is None:
        storage_client = _get_storage_client()

    if not check_bucket_exists(bucket_name):
        raise GoogleCloudStorageBucketNotFoundError(f"{bucket_name} does not exist.")

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    return blob.exists()


class GCS_Storage(object):
    """A class for interacting with Google Cloud Storage.
    """
    def __init__(self):
        """Initialises the Google Cloud Storage client with additional Exception handling.

        Raises:
            GoogleCloudStoragePermissionError: If the user does not have permission to access the Google Cloud Storage bucket, for example if there is
                no credentials file or the credentials file is invalid.

        Returns:
            storage.Client: A Google Cloud Storage client instance.
        """
        self._client = _get_storage_client()

    def write(self, file_contents: Union[str, bytes], bucket_name: str, destination_filename: str):
        """Writes a file of either string or bytes content type to Google Cloud Storage.

        Args:
            file_contents (Union[str, bytes]): The contents of the file to write to Google Cloud Storage.
            bucket_name (str): The name of the Google Cloud Storage bucket to write the file to.
            destination_filename (str): The name of the file to write to Google Cloud Storage.

        Raises:
            GoogleCloudStorageResourceNotFoundError: If the Google Cloud Storage bucket does not exist.
        """
        write_file_to_gcs(file_contents=file_contents, bucket_name=bucket_name, destination_filename=destination_filename, storage_client=self._client)

    def write_json(self, json_dict: Dict[Any, Any], bucket_name: str, destination_filename: str):
        """Writes a JSON file to Google Cloud Storage.

        Args:
            json_dict (Dict[Any, Any]): The dictionary to export as JSON to Google Cloud Storage.
            bucket_name (str): The name of the Google Cloud Storage bucket to write the file to.
            destination_filename (str): The name of the file to write to Google Cloud Storage. If it does not end with the .json extension, it will be added.

        Raises:
            ValueError: If the dictionary cannot be serialized to JSON.
        """
        write_json_to_gcs(json_dict=json_dict, bucket_name=bucket_name, destination_filename=destination_filename, storage_client=self._client)

    def read(self, bucket_name: str, origin_filename: str, read_mode: Literal["r", "b"] = "r") -> Union[bytes, str]:
        """Reads a file from Google Cloud Storage.

        Args:
            bucket_name (str): The name of the Google Cloud Storage bucket to read the file from.
            origin_filename (str): The name of the file to read from Google Cloud Storage.
            read_mode (Literal["r", "b"], optional): The mode to read the file in. "r" for text, "b" for bytes. Defaults to "r".

        Raises:
            GoogleCloudStorageResourceNotFoundError: If the Google Cloud Storage bucket or file does not exist.
            ValueError: If the read_mode is not "b" but the file cannot be decoded as UTF-8.

        Returns:
            Union[bytes, str]: The raw contents of the file.
        """
        return read_file_from_gcs(bucket_name=bucket_name, origin_filename=origin_filename, read_mode=read_mode, storage_client=self._client)

    def delete(self, bucket_name: str, destination_filename: str):
        """Deletes a file from Google Cloud Storage.

        Args:
            bucket_name (str): The name of the Google Cloud Storage bucket to delete the file from.
            destination_filename (str): The name of the file to delete from Google Cloud Storage.

        Raises:
            GoogleCloudStorageResourceNotFoundError: If the Google Cloud Storage bucket or file does not exist.
        """
        delete_file_from_gcs(bucket_name=bucket_name, destination_filename=destination_filename, storage_client=self._client)
