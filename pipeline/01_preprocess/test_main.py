import pytest

from main import remove_brackets, cut_tagged, cutter


@pytest.mark.parametrize(
    "input_text,expected",
    [
        ("[tag]\ntext", "text"),
        ("text[tag]", "text"),
        ("[tag1][tag2]text", "text"),
        ("text[tag1][tag2]", "text"),
        ("[tag1 text", ""),
        ("text tag]", ""),
        ("[tag1]text[tag2]", "text"),
        ("[tag1 some [nested] text]outside", "outside"),
        ("no tags here", "no tags here"),
        ("[open tag", ""),
        ("close tag]", ""),
    ],
)
def test_remove_brackets(input_text, expected):
    assert remove_brackets(input_text) == expected


def test_cut_tagged():
    # End bracket exists
    assert cut_tagged("[tag]text", 0) == "text"
    assert cut_tagged("abc[tag]text", 3) == "text"
    # End bracket at end
    assert cut_tagged("abc[tag]", 3) == ""
    # Leading whitespace and newline
    assert cut_tagged("[tag]\n text", 0) == "text"


def test_cutter():
    # Marker [Текст песни
    assert cutter("abc[Текст песни]text") == "text"
    # Marker Lyrics
    assert cutter("abcLyrics text") == "text"
    # No marker
    assert cutter("abc") == "abc"
    # Marker Lyrics at start
    assert cutter("Lyrics text") == "text"
    # Marker [Текст песни not at start
    assert cutter("foo [Текст песни]bar") == "bar"
