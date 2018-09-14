import datetime
import http.client
import unittest.mock as mock
from collections import namedtuple

import pytest

from query import Movie, Theater, format_movie_data, movie_data_query


# Query.py
class TestTheater:

    def setup(self):
        self.name = 'TEST'
        self.showtimes = ['{}:00pm'.format(i) for i in range(3)]
        self.theater = Theater(self.name, self.showtimes)

    def test_repr(self):
        assert self.theater.name == repr(self.theater)

    def test_theater_str(self):
        assert (
            str(self.theater)
            == '{}: {}'.format(self.theater.name, ', '.join(self.showtimes))
        )


class TestMovie:

    def setup(self):
        self.title = 'TEST'
        self.rating = 'pg'
        self.duration = '1hr and 30mins'
        self.movie = Movie(self.title, self.rating, self.duration)

    def test_repr(self):
        assert self.movie.title == repr(self.movie)

    def test_str(self):
        assert str(self.movie) == '{}, {}, {}'.format(
            self.title, self.rating, self.duration
        )

    def test_showtimes(self):
        """Test Movie.showtimes returns str(Theater), new line separated."""
        theaters = []
        theater_len = 3
        for i in range(theater_len):
            theater = Theater(
                'TEST {}'.format(i),
                ['{}:{}0pm'.format(x, i) for x in range(1, 4)]
            )
            theaters.append(theater)
            self.movie.theaters.append(theater)
        desired_results = (
            "{}\n{}\n{}"
            .format(str(theaters[0]), str(theaters[1]), str(theaters[2]))
        )
        assert self.movie.showtimes == desired_results


class TestMovieDataQuery:

    def setup(self):
        self.title = 'TEST'
        self.zip = 'test_zip'
        self.start_date = datetime.datetime.today().strftime('%m-%d-%Y')
        self.Response = namedtuple('Response', 'json')

    @mock.patch('query.requests.get')
    def test_movie_not_found(self, request_get_mock):
        request_get_mock.return_value = self.Response(
            {"Error": "Movie not found!"}
        )
        results = movie_data_query(
            t=self.title, zip=self.zip, start_date=self.start_date
        )
        import pdb; pdb.set_trace()
        movie_str = 'Movie info for {} not found.'.format(self.title.title())
        assert results == movie_str


class TestFormatMovieData:

    MOVIE_NOT_FOUND_TXT = "Couldn't find movie {title} in showtimes"

    def setup(self):
        self.movies = {}
        for i in range(3):
            title = 'TEST {}'.format(i)
            self.movies.update({title: Movie(title, 'r', '1hr 3{}'.format(i))})

    def test_movie_not_found(self):
        """Assert if movie not found, return error message."""
        title = 'NO MOVIE!'
        assert all(title != m.title for m in self.movies.values())
        assert (
            format_movie_data(self.movies, title)
            == self.MOVIE_NOT_FOUND_TXT.format(title=title)
        )

    def test_movie_found(self):
        """Assert if movie not found, return error message."""
        title = 'TEST 1'
        showtimes = ['{}:00pm'.format(i) for i in range(1, 4)]
        assert any(title == m.title for m in self.movies.values())

        self.movies[title].theaters.append(Theater('THEATER', showtimes))
        results = format_movie_data(self.movies, title)
        movie_str, showtime_str = results.split('\n')
        assert title.title() in movie_str
        assert all(st in showtime_str for st in showtimes)


# def test_split_line():
#     """Assert that function split_line in query.py divides the movie
#     information into the correct bins.
#     """
#     test_line = 'christopher robin (pg) · 1 hr 44 min'
#     m = Movie(test_line)
#     assert m.title == 'christopher robin'
#     assert m.rating == 'pg'
#     assert m.duration == '1 hr 44 min'
#
#     test_line = 'christopher robin'
#     m = Movie(test_line)
#     assert m.title == 'christopher robin'
#     assert m.rating == ''
#     assert m.duration == ''
