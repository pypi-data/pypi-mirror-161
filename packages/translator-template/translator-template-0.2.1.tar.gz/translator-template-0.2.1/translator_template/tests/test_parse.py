from io import StringIO

from translator_template.parse import read


def test_read():
    def read_from(s):
        with StringIO(s) as f:
            return [p for p in read(f)]

    assert [("PAGE 1", 2)] == read_from("2")
    assert [("PAGE 1", 2), ("PAGE 2", 3)] == read_from("23")
    assert [("PAGE 1", 2), ("PAGES 2-3", 3)] == read_from("23-")
    assert [("PAGE 1", 56)] == read_from("*56*")
    assert [("PAGES 1-2", 56), ("PAGE 3", 4)] == read_from("*56*-4")
    assert [("PAGE 1", 1), ("PAGE 2", 0), ("PAGE 3", 1)] == read_from("101")
    assert [("PAGE 1", 1), ("PAGE 2", 23), ("PAGE 3", 4)] == read_from("1*23*4")
    assert [("PAGE 1", 1), ("PAGE 2", 23), ("PAGE 3", 45)] == read_from("1*23**45*")
    assert [("PAGE 1", 1), ("PAGES 2-3", 23), ("PAGE 4", 45)] == read_from("1*23*-*45*")
