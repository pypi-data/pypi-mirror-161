"""Main file for Showing class and showing related functions."""
from datetime import datetime
from typing import List

import requests

from .cinema import Cinema
from .movie import Movie


class Showing:
    """Main class for showings that includes information about them."""

    def __init__(self, **kwargs) -> None:
        """Initialize a Showing object."""
        self.date_prefix = kwargs.get("date_prefix")
        self.day = kwargs.get("date_day")
        self.datetime = datetime.strptime(kwargs.get("date_time"), "%Y-%M-%D")
        self.cinema = Cinema(cinema_id=kwargs.get("cinema"))
        self.movie = Movie(movie_id=kwargs.get("movie"))

    def __str__(self) -> str:
        """Return a string representation of the Showing object."""
        return self.date_prefix


def get_showings() -> List[Showing]:
    """Return a list of Showing objects."""
    url = "https://www.myvue.com/data/showings/340436/10091"

    response = requests.request("GET", url).json()

    showings = []
    for day in response.get("showings", {}):
        for time in day.get("times", {}):
            day_without_showings = day.copy()
            day_without_showings.pop("times")
            day_without_showings.pop("is_dp2_2")

            showings.append(Showing(**time, **day_without_showings))

    return showings
