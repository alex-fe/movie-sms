import datetime
import unittest.mock as mock
from collections import namedtuple

import pytest
from bs4 import BeautifulSoup

from query import (
    NOT_FOUND_STR, Movie, Theater, format_movie_data, movie_data_query,
    showtimes_query, split_line
)


@pytest.mark.query
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


@pytest.mark.query
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


@pytest.mark.query
class TestMovieDataQuery:

    def setup(self):
        self.title = 'TEST'
        self.http_response = namedtuple('http_response', 'json')

    @mock.patch('query.requests.get')
    def test_movie_not_found(self, request_get_mock):
        request_get_mock.return_value = self.http_response(
            json={"Error": "Movie not found!"}
        )
        result_str = movie_data_query(t=self.title)
        assert (
            result_str ==
            NOT_FOUND_STR.format(id='Movie info', t=self.title.title())
        )

    @mock.patch('query.requests.get')
    def test_movie_found(self, request_get_mock):
        """Assert that the movie_str is correctly populated."""
        data = {
            'Title': self.title,
            'Rated': 'R',
            'Year': '2017',
            'Runtime': '1hr 20mins',
            'Genre': 'Test',
            'Director': 'Test Testington',
            'Actors': 'T. Test, Tessa Test',
            'Plot': self.test_movie_found.__doc__,
            'Metascore': '86',
            'imdbRating': '4.2',
            'Ratings': [{'Value': '54%'}]
        }
        request_get_mock.return_value = self.http_response(json=data)
        movie_str = movie_data_query(t=self.title)
        for x, y in data.items():
            if x != 'Ratings':
                assert y in movie_str
            else:
                assert y[0]['Value'] in movie_str


@pytest.mark.query
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


@pytest.mark.query
class TestShowtimesQuery:

    def setup(self):
        self.title = 'TEST'
        zipcode = '97211'
        date = datetime.datetime.today().strftime('%m-%d-%Y')
        self.kwargs = {'t': self.title, 'zip': zipcode, 'start_date': date}

    @mock.patch('urllib.request.urlopen')
    def test_showtimes_not_found(self, urlopen_mock):
        urlopen_mock.side_effect = ValueError()
        result_str = showtimes_query(**self.kwargs)
        assert (
            result_str ==
            NOT_FOUND_STR.format(id='Showtimes', t=self.title.title())
        )

    def test_split_line_complete_row(self):
        duration = '1 hr 30 min'
        rating = 'R'
        row = """
        <tr>
            <td>{}
                <div class="new_banner_printable">
                    <img src="" alt="New">
                </div>
                ({}) • {}
            </td>
        </tr>
        """.format(self.title, rating, duration)
        row_soup = BeautifulSoup(row, 'html.parser')
        results = split_line(row_soup)
        assert results[0] == self.title.lower()
        assert results[1] == rating.lower()
        assert results[2] == duration

    def test_split_line_incomplete_row(self):
        row = """
        <tr>
            <td colspan="2">
                Showtimes are currently not available for this theater.&nbsp;
                Please check back later.
            </td>
        </tr>
        """
        row_soup = BeautifulSoup(row, 'html.parser')
        results = split_line(row_soup)
        assert not results
