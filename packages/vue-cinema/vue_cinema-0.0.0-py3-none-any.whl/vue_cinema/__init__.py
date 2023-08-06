"""
vue_cinema package.

This package contains information about vue cinemas, movies and showings.
For now, this is only a wrapper around the vue cinema API. But, in the future
may have capability to book tickets and show seatings.
"""

from .cinema import (Cinema, get_cinema, get_cinemas,  # noqa: F401
                     search_cinemas)
from .movie import Movie, get_movie, get_movies  # noqa: F401
from .showing import Showing, get_showings  # noqa: F401
