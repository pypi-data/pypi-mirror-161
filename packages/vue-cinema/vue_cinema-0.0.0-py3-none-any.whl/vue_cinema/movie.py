"""Main file for Movie class and movie related functions."""
from datetime import datetime
from enum import Enum
from typing import List

import requests

from .shared import VueURL


class BBFC_Certificate(Enum):
    """Enum containing the different BBFC certificates."""

    _U = "U",
    _PG = "PG",
    _12 = "12",
    _12A = "12A",
    _15 = "15",
    _18 = "18"


class Movie:
    """Main class for movies that includes information about them."""

    def __init__(self, **kwargs) -> None:
        """Initialize a Movie object."""
        self.title = kwargs.get("title")
        self.id = int(kwargs.get("id", 0))
        self.image_hero = VueURL(kwargs.get("image_hero"))
        self.image_poster = VueURL(kwargs.get("image_poster"))
        self.cert = self._get_cert_type(kwargs.get("cert_image"))
        self.cert_description = kwargs.get("cert_desc")
        self.synopsis_short = kwargs.get("synopsis_short")
        self.synopsis_full = \
            self._remove_html(kwargs.get("synopsis_full", ""))
        self.release_date = kwargs.get("info_release")
        self.release_date = \
            datetime.strptime(self.release_date, "%d %b %Y")
        self.directors: List[str] | None = \
            self._split_names(kwargs.get("info_director", ""))
        self.cast: List[str] | None = \
            self._split_names(kwargs.get("info_cast", ""))
        self.runtime = kwargs.get("info_runningtime")
        self.trailers_link = VueURL(kwargs.get("videolink"))
        self.film_link = VueURL(kwargs.get("filmlink"))
        self.times_link = VueURL(kwargs.get("timeslink"))
        self.trailer_link = VueURL(kwargs.get("video"))
        self.coming_soon: bool = kwargs.get("coming_soon")
        self.genres = self._split_genres(kwargs.get("genres"))
        self.showing_type = kwargs.get("showing_type", {}).get("name")

    @classmethod
    def from_id(cls, movie_id: int) -> "Movie":
        """Return a Movie object from a movie id."""
        return get_movie(movie_id)

    def _get_cert_type(self, cert_url) -> BBFC_Certificate:
        rating = cert_url.split("/")[-1][:-4]

        match rating.upper():
            case "U": return BBFC_Certificate._U
            case "PG": return BBFC_Certificate._PG
            case "12": return BBFC_Certificate._12
            case "12A": return BBFC_Certificate._12A
            case "15": return BBFC_Certificate._15
            case "18": return BBFC_Certificate._18
            case "_": return None

    def _split_names(self, names: str) -> List[str]:
        if names:
            names = names.split(",")
            return [name.strip() for name in names]
        return None

    def _split_genres(self, genres) -> List[str]:
        return [genre for genre in genres.get("names")]

    def _remove_html(self, text: str) -> str:
        if text:
            return text\
                .replace("<p> </p>", "")\
                .replace("<p>", "")\
                .replace("</p>", "\n").strip()
        else:
            return None

    def __repr__(self) -> str:
        """Return a string representation of the Movie object."""
        return f"{self.title} ({self.release_date.year})"

    def __str__(self) -> str:
        """Return a string representation of the Movie object."""
        return self.title


def get_movies() -> List[Movie]:
    """Return a list of Movie objects found on the API."""
    url = "https://www.myvue.com/data/films"
    headers = {"x-requested-with": "XMLHttpRequest"}
    response = requests.request("GET", url, headers=headers).json()

    movies = []
    for movie in response.get("films"):
        movies.append(Movie(**movie))

    return movies


def get_movie(movie_id: int) -> Movie:
    """Return a Movie object with the id provided."""
    movies = get_movies()
    return [movie for movie in movies if movie.id == movie_id][0]
