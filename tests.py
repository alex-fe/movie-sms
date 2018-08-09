import pytest

from query import Movie, sum_ratings


def test_sum_ratings():
    """Assert sum_ratings acurately sums the receiption from the three provided
    sources.
    """
    values = [78, 81, 77]
    test_data = {
        'Metascore': str(values[0]),
        'imdbRating': str(values[1] / 10),
        'Ratings': [None, {'Value': '{}%'.format(values[2])}]
    }
    expected = round(sum(values) / len(values))
    assert expected == sum_ratings(test_data)


def test_split_line():
    """Assert that function split_line in query.py divides the movie
    information into the correct bins.
    """
    test_line = 'christopher robin (pg) · 1 hr 44 min'
    m = Movie(test_line)
    assert m.title == 'christopher robin'
    assert m.rating == 'pg'
    assert m.duration == '1 hr 44 min'

    test_line = 'christopher robin'
    m = Movie(test_line)
    assert m.title == 'christopher robin'
    assert m.rating == ''
    assert m.duration == ''


# class TestClass(object):
#     def test_one(self):
#         x = "this"
#         assert 'h' in x
#
#     def test_two(self):
#         x = "hello"
#         assert hasattr(x, 'check')
