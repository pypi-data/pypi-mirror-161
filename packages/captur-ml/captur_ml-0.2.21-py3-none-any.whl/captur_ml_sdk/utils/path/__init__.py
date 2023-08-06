class GsUri(object):
    def __init__(self, gs_uri: str):
        """Object representing a Google Storage URI.

        Args:
            gs_uri (str): Google Storage URI.

        Raises:
            ValueError: Raised if gs_uri is not a valid Google Storage URI.
        """
        if not gs_uri.startswith("gs://"):
            raise ValueError(f"{gs_uri} is not a valid Google Storage URI.")
        self.gs_uri = gs_uri

    def get_bucket(self) -> str:
        """Extracts the Bucket name.

        Returns:
            str: Google Storage Bucket.
        """
        return self.gs_uri.split("/")[2]

    def get_filepath(self) -> str:
        """Extracts the filepath after the Bucket name.

        Returns:
            str: Filepath of the Google Storage URI.
        """
        return "/".join(self.gs_uri.split("/")[3:])


class GsHttp(object):
    def __init__(self, http_url: str):
        """Object representing a HTTP(S) URL to a file in Google Storage.

        Args:
            http_url (str): HTTP URL to file in Google Storage.

        Raises:
            ValueError: Raised if http_url is not a valid HTTP URL.
        """
        if not http_url.startswith("http://storage.googleapis.com/")\
                and not http_url.startswith("https://storage.googleapis.com/"):
            raise ValueError(f"{http_url} is not a valid HTTP URL.")
        self.http_url = http_url

    def convert_to_gs_uri(self) -> str:
        """Converts the HTTP URL to a Google Storage URI.

        Returns:
            str: Google Storage URI.
        """
        gs_uri = self.http_url.replace("https://storage.googleapis.com/", "gs://")
        return gs_uri
