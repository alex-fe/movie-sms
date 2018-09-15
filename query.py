import re
import urllib.parse
import urllib.request

import requests
from bs4 import BeautifulSoup

from private_info import OMDB_API_KEY

OMDB_LINK = 'http://www.omdbapi.com/'
FANDANGO_LINK = (
    'https://www.fandango.com/theaterlistings-prn.aspx?'
    'location={0[zip]}&pn=1&sdate={0[start_date]}&'
    'tid=AAAPP,AAJMM,AAIJQ,AANJV,AAWPB,AAHIP,AANVP,AAHIF,AAHIJ,AAUHN'
)
NOT_FOUND_STR = '{id} for {t} not found.'


class Theater(object):
    def __init__(self, name, showtimes):
        self.name = name
        self.showtimes = showtimes

    def __str__(self):
        return '{}: {}'.format(self.name, ', '.join(self.showtimes))

    def __repr__(self):
        return self.name


class Movie(object):
    def __init__(self, title, rating, duration):
        self.title = title
        self.rating = rating
        self.duration = duration
        self.theaters = []

    @property
    def showtimes(self):
        return '\n'.join(str(t) for t in self.theaters)

    def __str__(self):
        """Print Movie instance as descriptive features."""
        return ', '.join(
            val for val in self.__dict__.values()
            if val and not isinstance(val, list)
        )

    def __repr__(self):
        return self.title


def movie_data_query(**kwargs):
    """Query OMDB for information on passed film.
    Args:
        kwargs (dict): Arguments for query.
    Returns:
        Movie data in formatted string.
    """
    kwargs.update({'apikey': OMDB_API_KEY})
    link = '?'.join((OMDB_LINK, urllib.parse.urlencode(kwargs)))
    json = requests.get(link).json
    if json.get('Error', '') == 'Movie not found!':
        return NOT_FOUND_STR.format(id='Movie info', t=kwargs['t'].title())
    else:
        return (
            "{0[Title]}\n{0[Rated]}, {0[Year]}, {0[Runtime]}\n{0[Genre]}\n"
            "Director: {0[Director]}\nCast: {0[Actors]}\n{0[Plot]}\n"
            "Metascore: {0[Metascore]}\nIMDB: {0[imdbRating]}\n"
            "Rotten Tomatoes: {0[Ratings][0][Value]}\n\n"
            "----------\n"
            "To receive showtimes in your area for this film, please respond "
            "SHOWTIMES and the zipcode. E.g. SHOWTIMES 97211"
        ).format(json)


def format_movie_data(movies, title):
    """Find film and create string representation.
    Args:
        movies (dict): Nested dict of films and showtimes.
        title (str): Title of desired movie.
    Returns:
        String with movie title and times.
    """
    try:
        selection = next(mov for mov in movies.values() if title in mov.title)
    except StopIteration:
        return "Couldn't find movie {} in showtimes".format(title)
    else:
        movie = movies[selection.title]
        return '\n'.join([str(movie).title(), movie.showtimes])


def split_line(line):
    """Split the movie information into its correct variables.
    Args:
        line (str): Movie information condensed into passed string.
    """
    if not all(char in line for char in ['hr', 'min', '(', ')']):
        title = line
        duration = ""
        rating = ""
    else:
        items = re.split('\W+', line)
        title = ' '.join(items[:-5])
        duration = ' '.join(items[-4:])
        rating = items[-5:-4][0]
    return title, rating, duration


def showtimes_query(**kwargs):
    """Scrape showtimes from site and return data.
    Args:
        kwargs (dict): Arguments for query.
    Returns:
        Movie data in formatted string.
    """
    req = urllib.request.Request(
        FANDANGO_LINK.format(kwargs), headers={'User-Agent': 'Mozilla/5.0'}
    )
    try:
        html = urllib.request.urlopen(req)
    except ValueError:
        return NOT_FOUND_STR.format(id='Showtimes', t=kwargs['t'].title())
    else:
        soup = BeautifulSoup(html, 'html.parser')
        movies = {}
        for theater_table in soup.find_all('table'):
            theater = theater_table.find('h4').text.strip()
            for row in theater_table.find_all('tr')[1:]:
                movie_line = ' '.join(row.find('td').text.split()).lower()
                title, rating, duration = split_line(movie_line)
                movie = movies.get(title, Movie(title, rating, duration))
                showtimes = [st.text for st in row.find_all('span')]
                movie.theaters.append(Theater(theater, showtimes))
                if movie not in movies:
                    movies[title] = movie
        return format_movie_data(movies, kwargs['t'])
