import json
import urllib.parse
import urllib.request

from private_info import OMDB_API_KEY

OMDB_LINK = 'http://www.omdbapi.com/'


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
