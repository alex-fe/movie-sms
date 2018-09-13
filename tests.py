import pytest

from query import Movie, Theater


# Query.py
class TestTheater(object):

    def setup(self):
        self.name = 'TEST'
        self.showtimes = ['{}:00pm'.format(i) for i in range(3)]
        self.theater = Theater(self.name, self.showtimes)

    def test_repr(self):
        assert self.theater.theater == repr(self.theater)

    def test_theater_str(self):
        assert (
            str(self.theater)
            == '{}: {}'.format(self.name, ', '.join(self.showtimes))
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
