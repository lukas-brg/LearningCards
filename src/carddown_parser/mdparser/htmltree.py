from __future__ import annotations
import textwrap

from typing import Generator

from ..errors import try_read_file
from ..config import get_config


config = get_config()

# Subtrees starting with these tags are never printed in a single line
NEWLINE_TAGS = ["div", "ul", "ol", "table",
                "thead", "tbody", "tr", "body", "br", "form"]
INLINE_TAGS = ["b", "em", "s", "mark", "sub", "sup"]
HTML_WHITESPACE = "&nbsp;"


class HtmlNode:

    def __init__(self, tag: str, *children: HtmlNode | str, **attributes: str):

        self.tag = tag
        self.children: list[HtmlNode] = []
        self.add_children(*children)
        self.attributes = attributes
        self.parent: HtmlNode | None = None
        self.boolean_attributes: set[str] = set()

    def __iter__(self):
        yield self
        for child in self.children:
            for node in child:
                yield node

    def parents(self) -> Generator[HtmlNode]:
        current_node = self
        while current_node is not None:
            yield current_node
            current_node = current_node.parent

    def remove_from_tree(self):
        self.parent.children.remove(self)
        self.parent = None

    def set_children(self, children: list[HtmlNode | str]):
        for c in children:
            c.parent = self
        _ = self.detach_children()
        self.children = children

    def replace_in_tree(self, node: HtmlNode | str):

        if isinstance(node, str):
            node = TextNode(node)

        index_self = self.parent.children.index(self)
        self.parent.children[index_self] = node
        node.parent = self.parent
        self.parent = None

    def add_children(self, *children: HtmlNode | str):
        """Always use either the HtmlNode constructor or this method to add children to a node,
           as it automatically sets the children's parent attributes
            and converts strings to TextNodes.
        """
        for c in children:
            if not c:
                continue
            if isinstance(c, str):
                text_node = TextNode(c)
                text_node.parent = self
                self.children.append(text_node)
            else:
                c.parent = self
                self.children.append(c)

    def detach_children(self) -> list[HtmlNode]:
        for child in self.children:
            child.parent = None
        return self.children

    def has_parent_with_tag(self, tag: str) -> bool:
        return any(tag == parent.tag for parent in self.parents())

    def search_parents_by_attribute(self, tag=None, substring_search=True, find_all=True, **attrs) -> Generator[HtmlNode]:

        for current_node in self.parents():
            for attr, val in attrs.items():
                if attr in current_node.attributes and (tag is None or current_node.tag == tag):
                    current_node_attr = current_node.attributes[attr]
                    if current_node_attr == val:
                        yield current_node

                        if not find_all:
                            return

                    elif substring_search and val in current_node_attr.lower():
                        yield current_node

                        if not find_all:
                            return

    def search_by_attribute(self, attr: str, value: str, substring_search=True, find_all=True) -> Generator[HtmlNode]:

        for node in self:
            if attr in node.attributes:
                if node.attributes[attr] == value:
                    yield node
                    if not find_all:
                        return
                elif substring_search and value in node.attributes[attr]:
                    yield node
                    if not find_all:
                        return

    def get_inner_text(self) -> str:
        text = " ".join(node.text.replace(HTML_WHITESPACE, " ")
                        for node in self if isinstance(node, TextNode))
        return text

    def contains_text(self) -> bool:
        return self.get_inner_text().strip() != ""

    def _attr_str(self) -> str:
        s = ""
        for key, value in self.attributes.items():
            # Reserved keywords like 'class' are prefixed with 'set_'
            if key.startswith("set_"):
                key = key[4:]  # e.g. HtmlNode("div", set_class="content")
            s += f' {key}="{value}"'
        return s

    def _boolean_attr_str(self) -> str:
        return "".join(" " + attr for attr in self.boolean_attributes)

    def __str__(self, depth=1, inline=False):
        start_tag = f"<{self.tag}{self._attr_str()}{self._boolean_attr_str()}>"
        end_tag = f"</{self.tag}>"
        indentation = ' ' * config.document.indent_html * depth

        if not inline and self.tag in NEWLINE_TAGS:
            children_str = "".join(
                c.__str__(depth+1) + "\n" for c in self.children)
            return f"{indentation}{start_tag}\n{children_str}{indentation}{end_tag}"
        else:
            indentation = indentation if not inline else ""
            children_str = ''.join(c.__str__(depth, inline=True)
                                   for c in self.children)
            return f"{indentation}{start_tag}{children_str}{end_tag}"


class SelfClosingTag(HtmlNode):

    def __str__(self, depth=0, inline=False):

        indentation = ' ' * depth * config.document.indent_html
        tag = f"<{self.tag}{self._attr_str()}{self._boolean_attr_str()}/>"

        if inline:
            return tag

        return indentation + tag


class TextNode(HtmlNode):
    def __init__(self, text: str, preserve_whitespace=False):
        if preserve_whitespace:
            text = text.replace("\t", HTML_WHITESPACE *
                                config.mdparser.tabsize)
            text = text.replace(" ", HTML_WHITESPACE)

        self.tag = "text"
        self.children = []
        self.text: str = text
        self.attributes = {}

    def __str__(self, depth=0, inline=False):
        if inline:
            return self.text
        else:
            return ' ' * depth * config.document.indent_html + self.text


class WhiteSpaceNode(TextNode):
    def __init__(self, spaces: int):
        super().__init__(
            text=HTML_WHITESPACE * spaces
        )


class HtmlFile:
    def __init__(self, script_files=None, style_files=None, title="", style_str="", head_str="", script_str="", charset="utf-8", lang="en"):
        self.body = HtmlNode('body', set_class=config.document.body_class)
        self.script_files = script_files or []
        self.style_files = style_files or []
        self.title = title
        self.style_str = style_str
        self.head_str = head_str
        self.script_str = script_str
        self.charset = charset
        self.lang = lang
        self._align_str = ""

    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            f.write(str(self))

    def set_alignment(self, margin: int, align: str):
        width = 100 - margin
        width_fhd = int(width / 100 * 1920)

        self._align_str = f"""
        .{config.document.body_class} {{ 
            width: {width}%;    

            margin-right: auto;
            margin-left: {'auto' if align == "center" else '15px'};
        }}
        
        @media only screen and (max-width: {width_fhd}px) {{
            .{config.document.body_class} {{
                width: 92%;
            }}
        }}
        
        @media only screen and (min-width: {width_fhd+1}px) and (max-width: 1920px){{
            .{config.document.body_class} {{
                width: {width_fhd}px;
                max-width: 92%;
        
            }}
        }}

        @media only screen 
        and (max-width: 480px) and (orientation: portrait) {{
            .{config.document.body_class} {{
                width: 95%;
    
            }}

            
            .{config.document.body_class} pre {{
                font-size: 14px; 
            }}

        
            .{config.document.body_class} table {{
                font-size: 14px; 
            }}
    
        }}

        """

    def __str__(self) -> str:
        style = "\n".join(try_read_file(style_path)
                          for style_path in self.style_files)
        script = "\n".join(try_read_file(script_path)
                           for script_path in self.script_files)

        style_section = f"""
    <style>
{textwrap.indent(style, ' ' * 12)}
{textwrap.indent(self._align_str, ' ' * 12)}
{textwrap.indent(self.style_str, ' ' * 12)}
    </style>
"""
        script_section = f"""
    <script>
{textwrap.indent(script, ' ' * 12)}
{textwrap.indent(self.script_str, ' ' * 12)}
    </script>
"""

        self.body.add_children(style_section, script_section)

        return f"""
<!DOCTYPE html>
<html lang="{self.lang}">
    <head>

        <script>
            MathJax = {{
            tex: {{
                inlineMath: [['$', '$']],
                displayMath: [['$$', '$$']]
            }},
            svg: {{
                fontCache: 'global'
            }}
            }};
        </script>

        <meta charset="{self.charset}">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Source+Code+Pro:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap">

        <title>{self.title}</title>
        {self.head_str} 
    
    </head>

{self.body}

</html>
"""
