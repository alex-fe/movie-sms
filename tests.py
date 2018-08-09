import pytest

from query import Movie


def test_split_line():
    """Assert that function split_line in query.py divides the movie
    information into the correct bins.
    """
    test_line = 'Christopher Robin (PG) · 1 hr 44 min'
    m = Movie(test_line)
    assert m.title == 'christopher robin'
    assert m.rating == 'pg'
    assert m.duration == '1 hr 44 min'


# class TestClass(object):
#     def test_one(self):
#         x = "this"
#         assert 'h' in x
#
#     def test_two(self):
#         x = "hello"
#         assert hasattr(x, 'check')
