import collections
import json
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
    data = json.load(urllib.request.urlopen(link))
    movie_str = """
    {0[Title]}
    {0[Rated]}, {0[Year]}, {0[Runtime]}
    {0[Genre]}
    Director: {0[Director]}
    Cast: {0[Actors]}
    Plot: {0[Plot]}
    Rating: {1}%
    """
    return movie_str.format(data, sum_ratings(data))


def format_movie_data(movies, title):
    """Find film and create string representation.
    Args:
        movies (dict): Nested dict of films and showtimes.
        title (str): Title of desired movie.
    Returns:
        String with movie title and times.
    """
    selection = next(mov for mov in movies.keys() if title in mov.lower())
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
    html = urllib.request.urlopen(req)
    soup = BeautifulSoup(html, 'html.parser')
    movies = collections.defaultdict(dict)
    for theater_table in soup.find_all('table'):
        theater = theater_table.find('h4').text.strip()
        for row in theater_table.find_all('tr')[1:]:
            name = ' '.join(row.find('td').text.split())
            showtimes = [
                st.text if 'p' not in st.text
                else st.text[:st.text.index('p') + 1]
                for st in row.find_all('li')
            ]
            movies[name].update({theater: showtimes})
    return format_movie_data(movies, kwargs['t'])
