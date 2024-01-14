import pytest
from src.carddown_parser.mdparser.mdparser import find_tokens
from src.carddown_parser.mdparser.htmltree import HtmlNode
from src.carddown_parser.mdparser.tokens import AutomaticLinkToken, EmphToken, BoldToken

def len_tokens(tokens, length):
    print(tokens.keys)
    return len(tokens) == length


def no_tokens(tokens):
    return len_tokens(tokens, 0)


def test_empty_tokens():
    string = "****"
    assert no_tokens(find_tokens(string))
    
    string = "__"
    assert no_tokens(find_tokens(string))
    
   
    string = "~~~~"
    assert no_tokens(find_tokens(string))
    
    string = "[]()"
    assert no_tokens(find_tokens(string))

    string = "[Link]()"
    assert no_tokens(find_tokens(string))
    
    string = "``"
    assert no_tokens(find_tokens(string))
    
    string = "===="
    assert no_tokens(find_tokens(string))



def test_unclosed_tokens():
    string = "**"
    assert no_tokens(find_tokens(string))

    string = "_"
    assert no_tokens(find_tokens(string))
    
    string = "~~"
    assert no_tokens(find_tokens(string))
    
    string = "`"
    assert no_tokens(find_tokens(string))

    string = "=="
    assert no_tokens(find_tokens(string))


def test_hr():
    string = "This is a line ***"
    assert no_tokens(find_tokens(string))
    
    string = "***"
    assert len_tokens(find_tokens(string), 1)


def test_link_token():
    string = "[Link](google.de)"
    tokens = find_tokens(string)

    assert len(tokens) == 1
    token = tokens[0]
    link = token.to_html()
    assert link.properties["href"] == "https://www.google.de"
    assert token.start == 0
    assert token.content_start == 1
    assert token.content_end == 5
    assert token.end == len(string) 

    string = "test string https://www.google.de test string"
    tokens = find_tokens(string)
    assert len(tokens) == 1
    assert 11 in tokens
    token = tokens[11]
    assert isinstance(token, AutomaticLinkToken)


def test_contentless_tokens():
    string = "*****"
    assert no_tokens(find_tokens(string))

    string = "_____"
    assert no_tokens(find_tokens(string))
    
    string = "~~~~~"
    assert no_tokens(find_tokens(string))
    
    string = "```"
    assert no_tokens(find_tokens(string))

    string = "====="
    assert no_tokens(find_tokens(string))


def test_multiple_tokens():
    string = "_Here_ is some _**Example**_ text to test **multiple** fontstyles in _one_ line"
    tokens = find_tokens(string)
    assert len(tokens) == 5

    assert 0 in tokens
    token = tokens[0]
    assert isinstance(token, EmphToken)
    assert token.start == 0
    assert token.content == "Here"
    assert token.content_start == 1
    assert token.content_end == 5
    assert token.end == 6

    assert 15 in tokens
    token = tokens[15]
    assert isinstance(token, EmphToken)
    assert token.content == "**Example**"
    assert token.content_start == 16
    assert token.content_end == 27
    assert token.end == 28


    assert 16 in tokens
    token = tokens[16]
    assert isinstance(token, BoldToken)
    assert token.content == "Example"
    assert token.content_start == 18
    assert token.content_end == 25
    assert token.end == 27

    assert 42 in tokens
    token = tokens[42]
    assert isinstance(token, BoldToken)
    assert token.content == "multiple"
    assert token.content_start == 44
    assert token.content_end == 52
    assert token.end == 54

    assert 69 in tokens
    token = tokens[69]
    assert isinstance(token, EmphToken)
    assert token.content == "one"
    assert token.content_start == 70
    assert token.content_end == 73
    assert token.end == 74
