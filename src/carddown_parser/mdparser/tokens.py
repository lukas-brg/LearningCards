import json
import os
from abc import ABC
from typing import Match
from carddown_parser.mdparser.htmltree import HtmlNode

from ..config import get_config

from .htmltree import HtmlNode, SelfClosingTag, TextNode
from .utils import find_subclasses

from .latex import latex_to_svg


with open(os.path.join(os.path.dirname(__file__), "emojis.json"), encoding="utf-8") as f:
    emojis: dict[str, str] = json.load(f)


config = get_config()


class InlineToken(ABC):
    """ Abstract base class for all InlineToken Types
       A subclass must define the `tag` and `pattern` attributes.

       Optionally the default values of the other attributes can be overridden.

       For maximum control a subclass may override the `create` and `to_html` methods.
    """
    tag: str
    patterns: list[str]

    # in case of wanting to match a pattern before the actual token starts, set number of chars before token here
    pre_chars: int = 0

    # content of token is in group one by default, can be overridden in subclass
    content_group: int = 1

    self_closing = False

    parse_content = True

    no_content = False

    attributes = {}

    def __init__(self, start, content_start: int, content_end: int, content: str, end: int, match: Match):
        self.start = start
        self.content_start = content_start
        self.content_end = content_end
        self.content = content
        self.end = end
        self.match = match

        self.on_create()

    @classmethod
    def create(TokenType, match: Match):
        start, end = match.span()
        if TokenType.no_content:
            content_start, content_end = end, end
            content = None
        else:
            content_start, content_end = match.span(TokenType.content_group)
            content = match.group(TokenType.content_group)

        return TokenType(
            start=start + TokenType.pre_chars,
            content_start=content_start,
            content_end=content_end,
            content=content,
            end=end,
            match=match
        )

    def on_create(self):
        """This method can be overriden by a subclass, if it needs to modify anything about the token instance"""
        pass

    @staticmethod
    def get_all_token_types() -> list[type]:
        return find_subclasses(InlineToken)

    def to_html(self) -> HtmlNode:
        return HtmlNode(self.tag, **self.attributes) if not self.self_closing else SelfClosingTag(self.tag, **self.attributes)


class InlineHtmlToken(InlineToken):
    patterns = [
        r"(<.+>)"
    ]
    no_content = True

    def to_html(self) -> HtmlNode:
        return TextNode(self.match.group(1))


class LinkToken(InlineToken):
    tag = "a"
    patterns = [r"(?:^|[^!])\[(.*?)\]\((.*?)(?:\s*\"(.*?)\")?\)"]

    def on_create(self):
        # To make sure an ImageToken isn't matched, this token test for either the start of the line or a character that is not '!'
        # But since it can't be known which it is the start of the match doesn't necessarily equal the start of the token, so it is determined based on the content
        # The same is done for every token that needs to rule out a character before like this
        self.start = self.content_start - 1

    def to_html(self):
        url = self.match.group(2)
        title = self.match.group(3) or ""
        if self.content.strip() == "":
            self.content = url
            self.content_start, self.content_end = self.match.span(2)
            self.parse_content = False

        if not url.startswith("#") and not url.startswith("http") and not url.startswith("./"):
            url = "http://" + url

        return HtmlNode(self.tag, href=url, title=title)


class ImageToken(InlineToken):
    tag = "img"
    no_content = True
    patterns = [r"!\[(.*?)\]\((.*?)(?:\s*\"(.*?)\")?\)"]

    def to_html(self):
        title = self.match.group(3) or ""
        alt = self.match.group(1)
        src = self.match.group(2)
        max_width = f"max-width: {config.document.image_max_width}"
        return SelfClosingTag(self.tag, alt=alt, src=src, title=title, style=max_width)


class AutomaticLinkToken(InlineToken):
    tag = "a"
    patterns = [r"(?:^|[^(])(https?://[^\s,]+)"]
    no_content = True

    def on_create(self):
        self.start, _ = self.match.span(1)

    def to_html(self):
        url = self.match.group(1)
        return HtmlNode(self.tag, url, href=url)


class BoldToken(InlineToken):
    tag = "strong"
    patterns = [
        r"\*\*(.+?)\*\*",
        r"__(.+?)__"
    ]


class EmphToken(InlineToken):
    tag = "em"
    patterns = [
        r"(?:^|[^_])_([^_\[\]:/]+)\_",
        r"(?:^|[^\*])\*([^\*]+)\*"
    ]

    def on_create(self):
        self.start = self.content_start - 1


class StrikeToken(InlineToken):
    tag = "s"
    patterns = [r"~~(.+?)~~"]


class CodeToken(InlineToken):
    tag = "code"
    patterns = [r"`([^`]+)`"]
    parse_content = False
    no_content = True

    def to_html(self) -> HtmlNode:
        code_str = self.match.group(1)
        code_str = code_str.replace("<", "&lt;")
        code_str = code_str.replace(">", "&gt;")

        if config.mdparser.prettyprint_inline_code:
            return HtmlNode(self.tag, code_str, set_class="prettyprint inline")
        return HtmlNode(self.tag, code_str, **self.attributes, set_class="inline")


class SubscriptToken(InlineToken):
    tag = "sub"
    pre_chars = 1
    patterns = [r"[\S]~([^~\\\{\}]+)~"]


class SuperscriptToken(InlineToken):
    tag = "sup"
    patterns = [r"\^([^\^\\\{\}]+)\^"]


class HighlightToken(InlineToken):
    tag = "mark"
    patterns = [r"==([^=]+)=="]


class RightArrowToken(InlineToken):
    patterns = [r"-->"]
    no_content = True

    def to_html(self) -> HtmlNode:
        return HtmlNode("span", "&#8594;")


class InlineEquationToken(InlineToken):
    patterns = [r"(\$.+?\$)"]
    parse_content = False
    tag = "span"
    no_content = True

    def to_html(self) -> HtmlNode:
        equation = self.match.group(1)
        if config.document.prerender_latex is False:
            equation = equation.replace("<", "&lt;")
            equation = equation.replace(">", "&gt;")
            return TextNode(equation)
        else:
            svg_data = latex_to_svg(equation[1:-1])
            return HtmlNode("span", svg_data, set_class="latex inline-latex")


class FootNoteReferenceToken(InlineToken):
    patterns = [r"\[\^(\S+)\]($|[^:])"]
    tag = "a"
    no_content = True

    def to_html(self) -> HtmlNode:
        _, end = self.match.span(1)
        self.end = end + 1
        text = self.match.group(1)
        href = f"#footnote-{text}"
        display_text = "[" + text + "]"
        a = HtmlNode(self.tag, display_text, href=href,
                     set_class="footnote-ref", id="ref-" + text)
        return HtmlNode("sup", a)


class EmojiToken(InlineToken):
    patterns = [r"(:[a-zA-Z0-9_\-]+:)"]
    parse_content = False

    def to_html(self) -> HtmlNode:
        text = emojis.get(self.content, self.content)
        return TextNode(text)
