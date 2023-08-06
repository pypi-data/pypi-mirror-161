import io
import base64
import urllib

from PIL import Image as PILImage
from typing import Union
from urllib.error import URLError

from captur_ml_sdk.dtypes.generics import Image

def resize_image_by_factor(image: PILImage.Image, factor: float):
    """Changes the size of the image by a factor, preserving the aspect ratio.

    Args:
        image (PIL Image): Image to be resized.
        factor (float): Factor that both width and height are multiplied by.

    Returns:
        image (PIL Image): resized image.
    """
    if not isinstance(image, PILImage.Image):
        input_type = type(image)
        raise TypeError(f"image is of type {input_type} but must be a PIL Image")
    if not isinstance(factor, float):
        input_type = type(factor)
        raise TypeError(f"factor is of type {input_type} but must be a float")
    w, h = image.size
    neww, newh = int(w * factor), int(h * factor)
    image = image.resize((neww, newh))
    return image

def convert_pil_image_to_bytes_array(image: PILImage.Image, encode_as_utf8: bool = False, image_format: str = "jpeg"):
    """Converts PIL image to bytes array.

    Args:
        image (PIL.Image): Image to be converted to a bytes array.

    Returns:
        bytes: Bytes array of the image.
    """
    if not isinstance(image, PILImage.Image):
        input_type = type(image)
        raise TypeError(f"image is of type {input_type} but must be a PIL Image")
    imgByteArr = io.BytesIO()
    image.save(imgByteArr, format=image_format)
    image_data = imgByteArr.getvalue()

    if encode_as_utf8:
        image_data = base64.b64encode(image_data).decode("utf-8")

    return image_data

def load_image_from_url(image_url: str, limit_image_size_to: int = 0, return_pil: bool = False) -> Union[PILImage.Image, Image]:
    """Retrieve an image via HTTP/S.

    Args:
        url (string): The http[s]://___ URL hosting the pure image data (i.e. not an HTML webpage, for example)
        limit_image_size_to (int, optional): If bigger than 0, limit the number of bytes of the image by rescaling. For example,
            a value of 1024 will reduce the image size (and quality) to fit into 1kB. NOTE: If this value is not 0, the image
            may be converted to JPEG depending on whether or not the resize operation is performed; if this is undesirable, set
            `return_pil` to True and convert to bytestring manually. Defaults to 0.
        return_pil (bool, optional): If True a PIL.Image instance will be returned, if False a captur_ml_sdk.dtypes.Image containing
            the UTF8-encoded string of the image data will be returned. Defaults to False.

    Raises:
        URLError: If the image cannot be retrieved from the URL.

    Returns:
        Image (Union[PIL.Image.Image, captur_ml_sdk.dtypes.Image]): If `return_pil` is True, a PIL.Image instance of the image is 
            returned, otherwise a captur_ml_sdk.dtypes.Image is returned.
    """
    try:
        with urllib.request.urlopen(image_url) as u:
            content_length = u.info().get(name="Content-Length")

            if content_length is None:
                raise URLError()

            image_size = int(content_length)
            rescale_factor = 0 if limit_image_size_to <= 0 or image_size < limit_image_size_to else limit_image_size_to / image_size

            if rescale_factor == 0:
                if return_pil:
                    return PILImage.open(u)

                image_data = u.read()
                image_data = base64.b64encode(image_data).decode("utf-8")
                image_data = Image(url=image_url, data=image_data)
            else:
                image_data = PILImage.open(u)
                image_data = resize_image_by_factor(image_data, rescale_factor)

                if return_pil:
                    return image_data

                image_data = convert_pil_image_to_bytes_array(image_data, encode_as_utf8=True)
                image_data = Image(url=image_url, data=image_data)

            return image_data
    except URLError:
        raise URLError(f"Could not retrieve image from url: {image_url}")
