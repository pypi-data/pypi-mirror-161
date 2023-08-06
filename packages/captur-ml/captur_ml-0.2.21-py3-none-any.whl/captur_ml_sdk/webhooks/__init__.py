import base64
import json
import pydantic
import requests

from typing import Dict, Union


def send_payload_to_webhook(webhook_url: str, payload: Union[Dict, pydantic.BaseModel]):
    """Sends a payload to a webhook.

    Args:
        webhook_url (str): URL of the webhook to send the event to.
        payload [Dict, pydantic.BaseModel]: Content to send to the webhook.

    Raises:
        ValueError: Raised if the payload is not a dictionary or pydantic.BaseModel
                    the post request fails.
    """
    if not isinstance(payload, dict):
        if isinstance(payload, pydantic.BaseModel):
            payload = payload.dict()
        else:
            raise ValueError("Payload must be a dictionary or a pydantic model.")
    try:
        requests.post(webhook_url, json=payload)
    except Exception:
        raise ValueError(f"Unable to post to {webhook_url}")


def push_published_message_to_webhooks(event, context):
    """Background Cloud Function to be triggered by Pub/Sub.
    Args:
         event (dict):  The dictionary with data specific to this type of
                        event. The `@type` field maps to
                         `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
                        The `data` field maps to the PubsubMessage data
                        in a base64-encoded string. The `attributes` field maps
                        to the PubsubMessage attributes if any is present.
         context (google.cloud.functions.Context): Metadata of triggering event
                        including `event_id` which maps to the PubsubMessage
                        messageId, `timestamp` which maps to the PubsubMessage
                        publishTime, `event_type` which maps to
                        `google.pubsub.topic.publish`, and `resource` which is
                        a dictionary that describes the service API endpoint
                        pubsub.googleapis.com, the triggering topic's name, and
                        the triggering event type
                        `type.googleapis.com/google.pubsub.v1.PubsubMessage`.
    Returns:
        None. The output is written to Cloud Logging.
    """
    pass
    event_data = json.loads(base64.b64decode(event['data']).decode('utf-8'))
    webhooks = event_data.get("webhooks")
    if not isinstance(webhooks, list):
        webhooks = [webhooks]
    event_content = event_data["content"]

    if not event_data:
        event_data = {
            "example_data": "Here is some example data that will in the future be read "
            "from the event message."
        }

    for url in webhooks:
        # This is where we actually make the requests aka trigger the relevant webhooks
        send_payload_to_webhook(url, event_content)

    return {
        "urls": webhooks,
        "body": event_content
    }
