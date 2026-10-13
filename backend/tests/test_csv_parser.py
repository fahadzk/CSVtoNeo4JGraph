import pytest
from backend.app.csv_parser import parse_csv_bytes

def test_quoted_commas_and_utf8():
    parsed = parse_csv_bytes('City,Note\n"New York","large, city"\n'.encode())
    assert parsed.headers == ["City", "Note"]
    assert parsed.rows == [["New York", "large, city"]]

def test_duplicate_headers_rejected():
    with pytest.raises(ValueError, match="unique"):
        parse_csv_bytes(b"a,a\n1,2\n")

def test_bad_width_warns_and_skips():
    parsed = parse_csv_bytes(b"a,b\n1\n2,3\n")
    assert parsed.row_count == 1
    assert "expected 2" in parsed.warnings[0]
