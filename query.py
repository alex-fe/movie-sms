import json
import re
import urllib.parse
import urllib.request

from bs4 import BeautifulSoup

from private_info import OMDB_API_KEY

OMDB_LINK = 'http://www.omdbapi.com/'
FANDANGO_LINK = (
    'https://www.fandango.com/theaterlistings-prn.aspx?'
    'location={0[zip]}&pn=1&sdate={0[start_date]}&'
    'tid=AAAPP,AAJMM,AAIJQ,AANJV,AAWPB,AAHIP,AANVP,AAHIF,AAHIJ,AAUHN'
)


class Theater(object):
    """docstring for Theater."""
    def __init__(self, theater, showtimes):
        self.theater = theater
        self.showtimes = showtimes

    def __str__(self):
        return self.theater


class Movie(object):
    """docstring for Movie."""
    def __init__(self, line):
        self.split_line(line)
        self.theaters = []

    def split_line(self, line):
        items = re.split('\W+', line.lower())
        self.title = ' '.join(items[:-5])
        self.duration = ' '.join(items[-4:])
        self.rating = items[-5:-4][0]

    def __str__(self):
        return self.title


def sum_ratings(data):
    """Average ratings from three sources used in OMDB data.
    Args:
        data (json): OMDB data in json format.
    Returns:
        Float rating average.
    """
    metascore = int(data['Metascore'])
    imdb_score = float(data['imdbRating']) * 10
    rotten_tomatoes_score = int(data['Ratings'][1]['Value'][:-1])
    return (metascore + imdb_score + rotten_tomatoes_score) / 3


def movie_data_query(**kwargs):
    """Query OMDB for information on passed film.
    Args:
        kwargs (dict): Arguments for query.
    Returns:
        Movie data in formatted string.
    """
    kwargs.update({'apikey': OMDB_API_KEY})
    link = '?'.join((OMDB_LINK, urllib.parse.urlencode(kwargs)))
    try:
        data = urllib.request.urlopen(link)
    except ValueError:
        movie_str = 'Movie info for {} not found.'.format(kwargs['t'])
    else:
        data = json.load(data)
        movie_str = """
        {0[Title]}
        {0[Rated]}, {0[Year]}, {0[Runtime]}
        {0[Genre]}
        Director: {0[Director]}
        Cast: {0[Actors]}
        Plot: {0[Plot]}
        Rating: {1}%
        """
        movie_str = movie_str.format(data, sum_ratings(data))
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
        selection = next(mov for mov in movies if title in mov.title)
    except StopIteration:
        return "Couldn't find movie {} in showtimes".format(title)
    else:
        showtimes = '\n'.join(
            "{}: {}".format(theater, ', '.join(st))
            for (theater, st) in movies[selection].items()
        )
        return '\n'.join((selection, showtimes))


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
        movies = []
        for theater_table in soup.find_all('table'):
            theater = theater_table.find('h4').text.strip()
            for row in theater_table.find_all('tr')[1:]:
                movie_line = ' '.join(row.find('td').text.split())
                showtimes = [st.text for st in row.find_all('span')]
                movie = Movie(movie_line)
                movie.theaters.append(Theater(theater, showtimes))
                movies.append(movie)
        return format_movie_data(movies, kwargs['t'])


if __name__ == '__main__':
    import datetime
    date = datetime.datetime.today().strftime('%m-%d-%Y')
    showtime_str = showtimes_query(
        t='Christopher Robin', zip='97211', start_date=date
    )
