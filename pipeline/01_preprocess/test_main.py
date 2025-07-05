import pytest
from main import remove_brackets

@pytest.mark.parametrize("input_text,expected", [
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
])
def test_remove_brackets(input_text, expected):
    assert remove_brackets(input_text) == expected
