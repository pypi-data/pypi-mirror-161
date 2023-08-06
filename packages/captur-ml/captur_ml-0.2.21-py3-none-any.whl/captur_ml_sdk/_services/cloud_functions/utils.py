import base64
import json
import pydantic


def parse_data_from_pubsub_message(
    event: bytes,
    pydantic_class: pydantic.main.ModelMetaclass
):
    """Parses data from a Pub/Sub message and raises an error if the
       message has an invalid format.

    Args:
        event (bytes): Base64-encoded Pub/Sub message.
        pydantic_class (pydantic.main.ModelMetaclass): A specified pydantic class.

    Raises:
        ValueError: Raised if the message has an invalid format.

    Returns:
        PydanticClass: An instance of the specified pydantic class.
    """
    data = json.loads(base64.b64decode(event['data']).decode('utf-8'))

    err = None
    try:
        event_data = pydantic.parse_obj_as(pydantic_class, data)
    except pydantic.ValidationError as e:
        err = e.errors()

    if err is not None:
        raise ValueError(f"Errors: {err}")

    return event_data
