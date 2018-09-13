import pytest

from query import Movie, Theater, format_movie_data


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


class TestFormatMovieData:

    MOVIE_NOT_FOUND_TXT = "Couldn't find movie {title} in showtimes"

    def setup(self):
        self.movies = {}
        for i in range(3):
            title = 'TEST {}'.format(i)
            self.movies.update({title: Movie(title, 'r', '1 hr 30')})

    def test_movie_not_found(self):
        """Assert if movie not found, return error message."""
        title = 'NO MOVIE!'
        assert all(title != m.title for m in self.movies.values())
        assert (
            format_movie_data(self.movies, title)
            == self.MOVIE_NOT_FOUND_TXT.format(title=title)
        )


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
