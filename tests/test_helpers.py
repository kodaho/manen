from manen.helpers import extract_integer


class TestExtractFigure:
    def test_extract_simple_integer(self):
        assert extract_integer("1") == 1
        assert extract_integer("0") == 0
        assert extract_integer("1234") == 1234
        assert extract_integer("01234") == 1234

    def test_extract_integer_with_text(self):
        assert extract_integer("1 thing") == 1
        assert extract_integer("0 thing") == 0
        assert extract_integer("10 things and more") == 10
        assert extract_integer("10 things and more...?!#") == 10

    def test_extract_integer_inside_text(self):
        assert extract_integer("You have 0 connection.") == 0
        assert extract_integer("You have 10 connections in your network.") == 10
        assert (
            extract_integer("If you want, you can have 12340new connections.") == 12340
        )

    def test_extract_integer_from_float(self):
        assert extract_integer("10,123.23") == 10123
        assert extract_integer("10.1") == 10
