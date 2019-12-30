import pytest
from arrow import ParserError
from datetime import date
from ..utils import strict_parse


def test_good():
    assert strict_parse("2012-09-21") == date(2012, 9, 21)
    assert strict_parse("1/4/15") == date(2015, 1, 4)
    assert strict_parse("1/14/15") == date(2015, 1, 14)
    assert strict_parse("12/11/2011") == date(2011, 12, 11)
    assert strict_parse("12/17/2011") == date(2011, 12, 17)


def test_slightly_funky_but_still_ostensibly_good():
    assert strict_parse("2002-10-18: 19:45") == date(2002, 10, 18)
    assert strict_parse("'2013-08-09") == date(2013, 8, 9)


def test_fails_on_incomplete():
    with pytest.raises(ParserError):
        strict_parse("2012")

    with pytest.raises(ParserError):
        strict_parse("2012-10")

    with pytest.raises(ParserError):
        strict_parse("3/2019")

    with pytest.raises(ParserError):
        strict_parse("3/2019")
