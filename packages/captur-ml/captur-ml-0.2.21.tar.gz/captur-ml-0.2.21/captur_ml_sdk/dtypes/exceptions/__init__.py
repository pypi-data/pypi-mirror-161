# ============ PubSub Exceptions ============ #
class GoogleCloudPubSubTopicDoesNotExistError(Exception):
    pass

# ============ Google Cloud Storage Exceptions ============ #
class GoogleCloudStoragePermissionError(Exception):
    pass
class GoogleCloudStorageResourceNotFoundError(Exception):
    pass
class GoogleCloudStorageBucketNotFoundError(Exception):
    pass

# ============ Google Cloud Vertex AI Endpoint Exceptions ============ #
class GoogleCloudVertexAIEndpointDoesNotExistError(Exception):
    pass
class GoogleCloudVertexAIEndpointImageTooLargeError(Exception):
    pass
class GoogleCloudVertexAIEndpointNoModelDeployedError(Exception):
    pass

# ============ Google Cloud Vertex AI General Exceptions ============ #
class GoogleCloudVertexAIModelDoesNotExistError(Exception):
    pass
class GoogleCloudVertexAIDatasetDoesNotExistError(Exception):
    pass
class GoogleCloudVertexAIResourceDoesNotExistError(Exception):
    pass
class GoogleCloudVertexAICompatibilityError(Exception):
    pass

# ============ Sentry Errors ============ #
class SentryDSNNotProvidedError(Exception):
    pass
