"""File containing code to be shared between classes."""
from urllib import parse


class VueURL:
    """Class for Vue URLs."""

    def __init__(self, url) -> None:
        """Initialize a VueURL object."""
        if url.startswith("/-/"):
            self.url = "https://www.myvue.com" + url
        elif url.startswith("//"):
            self.url = "https://" + url[2::]
        elif url.startswith("https://") or url.startswith("http://"):
            self.url = url
        elif url.startswith("/film"):
            self.url = "https://www.myvue.com" + url
        else:
            self.url = None

        if self.url:
            self.url = parse.quote(self.url, safe="%/:=&?~#+!$,;'@()*[]")

    def __str__(self) -> str:
        """Return a string representation of the VueURL object."""
        return self.url
