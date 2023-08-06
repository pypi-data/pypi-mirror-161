"""File for Cinema class and cinema related functions."""

from typing import List

import requests


class Cinema:
    """Main class for cinemas that includes information about them."""

    def __init__(self, **kwargs) -> None:
        """
        Initialize a Cinema object.

        If cinema_id is provided, then the Cinema is found using the API.
        """
        self.name = kwargs.get("name")
        self.search_term = kwargs.get("search_term")
        self.link_name = kwargs.get("link_name")
        self.id = int(kwargs.get("id", 0))

    @classmethod
    def from_id(cls, cinema_id: int) -> "Cinema":
        """Return a Cinema object from a cinema_id."""
        return get_cinema(cinema_id)

    def __str__(self) -> str:
        """Return a string representation of the Cinema object."""
        return self.name


def get_cinemas() -> List[Cinema]:
    """Return a list of Cinema objects."""
    url = "https://www.myvue.com/data/locations"
    headers = {"x-requested-with": "XMLHttpRequest"}

    response = requests.request("GET", url, headers=headers).json()

    cinemas = []
    for alpha in response.get("venues"):
        for cinema in alpha.get("cinemas"):
            cinemas.append(Cinema(**cinema))

    return cinemas


def get_cinema(cinema_id: int) -> Cinema | None:
    """Return a Cinema object with the provided ID."""
    cinemas = get_cinemas()
    try:
        return [cinema for cinema in cinemas if cinema.id == cinema_id][0]
    except IndexError:
        return None


def search_cinemas(search_term: str) -> List[Cinema]:
    """Return a list of Cinema objects that match the search term."""
    cinemas = get_cinemas()
    return [cinema for cinema in cinemas
            if search_term.lower() in cinema.search_term.lower()]
