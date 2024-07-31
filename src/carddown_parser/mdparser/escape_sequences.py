from collections import OrderedDict
from .htmltree import HtmlNode, TextNode
from ..config import get_config

config = get_config()

ESCAPE_SEQUENCES = { 
    r"\\": {
            "intermediate": "!!!ESCAPE!BACKSLASH!!!",
            "display_text": "\\"
    },
    "\*": {
            "intermediate": "!!!ESCAPE!ASTR!!!",
            "display_text": r"*"
    },
    "\_": {
            "intermediate": "!!!ESCAPE!UNDERSCORE!!!",
            "display_text": "_"
    },
    "\(": {
            "intermediate": "!!!ESCAPE!LPAREN!!!",
            "display_text": "("
    },
    "\)": {
            "intermediate": "!!!ESCAPE!RPAREN!!!",
            "display_text": ")"
    },
    "\[": {
            "intermediate": "!!!ESCAPE!LBRACKET!!!",
            "display_text": "["
    },
    "\]": {
            "intermediate": "!!!ESCAPE!RBRACKET!!!",
            "display_text": "]"
    },
    "\#": {
            "intermediate": "!!!ESCAPE!HASH!!!",
            "display_text": "#"
    },
    "\<": {
            "intermediate": "!!!ESCAPE!LT!!!",
            "display_text": "&lt;"
    },
    "\>": {
            "intermediate": "!!!ESCAPE!GT!!!",
            "display_text": "&gt;"
    },
    "\+": {
            "intermediate": "!!!ESCAPE!PLUS!!!",
            "display_text": "+"
    },
    "\!": {
            "intermediate": "!!!ESCAPE!BANG!!!",
            "display_text": "!"
    },
    "\~": {
            "intermediate": "!!!ESCAPE!TILDE!!!",
            "display_text": "~"
    },
    "\=": {
            "intermediate": "!!!ESCAPE!EQUAL!!!",
            "display_text": "="
    },
    "\`": {
            "intermediate": "!!!ESCAPE!BACKTICK!!!",
            "display_text": "`"
    },
    "\-": {
            "intermediate": "!!!ESCAPE!MINUS!!!",
            "display_text": "-"
    },
    
    "\|": {
            "intermediate": "!!!ESCAPE!PIPE!!!",
            "display_text": "|"
    },
    r"\\n": {
            "intermediate": "!!!ESCAPE!NEWLINE!!!",
            "display_text": '\\n'
    },
}

ESCAPE_SEQUENCES = OrderedDict(ESCAPE_SEQUENCES)


def escape_text(text: str):
    if config.document.prerender_latex is True:
        ESCAPE_SEQUENCES["\$"] = {"intermediate" : "!!!ESCAPE!DOLLARSIGN!!!", "display_text" : "$"}
    for str, esc in ESCAPE_SEQUENCES.items():
        text = text.replace(str, esc["intermediate"])
    return text


def unescape_text_in_tree(root: HtmlNode):
    for node in root:
        if isinstance(node, TextNode):
            for str, esc in ESCAPE_SEQUENCES.items():
                if node.has_parent_with_tag("code"):
                    node.text = node.text.replace(esc["intermediate"], str)
                else:
                    node.text = node.text.replace(esc["intermediate"], esc["display_text"])
