import json
import re
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup

from private_info import OMDB_API_KEY

COMMANDS = ['info', 'showtimes']
OMDB_LINK = 'http://www.omdbapi.com/'
FANDANGO_LINK = (
    'https://www.fandango.com/theaterlistings-prn.aspx?'
    'location={0[zip]}&pn=1&sdate={0[start_date]}&'
    'tid=AAAPP,AAJMM,AAIJQ,AANJV,AAWPB,AAHIP,AANVP,AAHIF,AAHIJ,AAUHN'
)


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
    data = json.loads(urllib.request.urlopen(link).read().decode('utf-8'))
    if data.get('Error', '') == 'Movie not found!':
        movie_str = 'Movie info for {} not found.'.format(kwargs['t'].title())
    else:
        ratings = {
            'metascore': data['Metascore'],
            'imdb': data['imdbRating'],
            'rotten_tomatoes': data['Ratings'][0]['Value']
        }
        movie_str = (
            "{0[Title]}\n{0[Rated]}, {0[Year]}, {0[Runtime]}\n{0[Genre]}\n"
            "Director: {0[Director]}\nCast: {0[Actors]}\n{0[Plot]}\n"
            "Metascore: {1[metascore]}\nIMDB: {1[imdb]}\n"
            "Rotten Tomatoes: {1[rotten_tomatoes]}\n\n"
            "----------\n"
            "To receive showtimes in your area for this film, please respond "
            "SHOWTIMES and the zipcode. E.g. SHOWTIMES 97211"
        )
        movie_str = movie_str.format(data, ratings)
    return movie_str


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
        return 'Showtimes for {} not found.'.format(kwargs['t'])
    else:
        soup = BeautifulSoup(html, 'html.parser')
        movies = {}
        for theater_table in soup.find_all('table'):
            theater = theater_table.find('h4').text.strip()
            for row in theater_table.find_all('tr')[1:]:
                movie_line = ' '.join(row.find('td').text.split()).lower()
                title, rating, duration = split_line(movie_line)
                print(title, rating, duration)
                movie = movies.get(title, Movie(title, rating, duration))
                showtimes = [st.text for st in row.find_all('span')]
                movie.theaters.append(Theater(theater, showtimes))
                if movie not in movies:
                    movies[title] = movie
        return format_movie_data(movies, kwargs['t'])
