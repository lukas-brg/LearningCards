import pytest
from src.carddown_parser.mdparser.htmltree import HtmlNode
from src.carddown_parser.mdparser.tokens import AutomaticLinkToken, EmphToken, BoldToken
from src.carddown_parser.mdparser.mdparser import *


ul_str = \
"""- ul 1
- ul2
-ul3
"""

ol_str = \
"""1. ol 1
2. ol2
3.ol3
"""

mix_str = \
"""1. ol
2. ol
- ul
- ul
"""

def test_list():
    list, i = parse_list(ul_str.split("\n"), 0)
    assert i == 2
    assert list.tag == "ul"
    assert len(list.children) == 2


    list, i = parse_list(ol_str.split("\n"), 0)
    assert i == 2
    assert list.tag == "ol"
    assert len(list.children) == 2

    list, i = parse_list(mix_str.split("\n"), 0)
    assert i == 2
    assert list.tag == "ol"
    assert len(list.children) == 2