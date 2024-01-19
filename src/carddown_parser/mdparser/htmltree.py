from __future__ import annotations
import  re
from typing import Generator

from ..errors import try_read_file
from ..config import get_config


config = get_config()

# Subtrees starting with these tags are never printed in a single line
NEWLINE_TAGS = ["div", "ul", "ol", "table", "thead", "tbody", "tr", "body"]
HTML_WHITESPACE = "&nbsp;"


class HtmlNode:
    
    def __init__(self, tag: str, *children: HtmlNode|str, **properties: str):
    
        self.tag = tag
        self.children: list[HtmlNode] = []
        self.add_children(*children) 
        self.properties = properties
        self.parent: HtmlNode = None


    def __iter__(self):
        yield self
        for child in self.children:
            for node in child:
                yield node


    def add_children(self, *children: HtmlNode|str):
        """Always use either the HtmlNode constructor or this method to add children to a node,
           as it automatically sets the children's parent attributes
            and converts strings to TextNodes.
        """
        for c in children:
            if not c:
                continue
            if isinstance(c, str):
                text_node = TextNode(c.strip())
                text_node.parent = self
                self.children.append(text_node)
            else:
                c.parent = self
                self.children.append(c)
    
    
    def search_parents_by_property(self, tag=None, substring_search=True, find_all=True, **props) -> Generator[HtmlNode]:
        current_node = self
        
        while current_node is not None:

            for prop, val in props.items():
                if prop in current_node.properties and (tag is None or current_node.tag == tag):
                    current_node_prop = current_node.properties[prop]
                    if current_node_prop == val:
                        yield current_node
    
                        if not find_all:
                            return
                    
                    elif substring_search and val in current_node_prop.lower():
                        yield current_node
                        
                        if not find_all:
                            return     
            
            current_node = current_node.parent    
            
 

    def search_by_property(self, prop: str, value: str, substring_search=True, find_all=True) -> Generator[HtmlNode]:
        
        for node in self:
            if prop in node.properties:
                if node.properties[prop] == value:
                    yield node
                    if not find_all:
                        return
                elif substring_search and value in node.properties[prop]:
                    yield node
                    if not find_all:
                        return
    

    
    def get_inner_text(self) -> str:
        text = " ".join(node.text.replace(HTML_WHITESPACE, " ") for node in self if isinstance(node, TextNode))
        return text
    

    def contains_text(self) -> bool:
        return self.get_inner_text().strip() != ""


    def _props_str(self) -> str:
        s = ""
        for key, value in self.properties.items():
            if key.startswith("set_"):  # Reserved keywords like 'class' are prefixed with 'set_'
                key = key[4:]  # e.g. HtmlNode("div", set_class="content")
            s += f' {key}="{value}"'
        return s


    def __str__(self, depth=1):

        indentation = ' ' * depth * config.document.indent_html        
        children = '\n'.join(c.__str__(depth+1) for c in self.children)
        start_tag = f"<{self.tag}{self._props_str()}>"
        end_tag = f"</{self.tag}>"
        
        if len(children.strip()) < 200 and self.tag not in NEWLINE_TAGS:
            
            children = re.sub("\n+", "", children)
            children = re.sub(r"\s+", " ", children)
            
            # Workaround to get superscript and subscript displayed right
            children = re.sub(r"(\S) <sup>", r"\1<sup>", children)
            children = re.sub(r"(\S) <sub>", r"\1<sub>", children)
            return indentation + start_tag + children.strip() + end_tag
      
        return indentation + start_tag + "\n" + children + "\n" + indentation + end_tag                                                                                           


class SelfClosingTag(HtmlNode):
   
    def __str__(self, depth=0):
        indentation = ' '* depth * config.document.indent_html 
        children_str = " ".join(str(c) for c in self.children)
        children_str = " " + children_str if len(children_str.strip()) > 0 else ""
        return f"{indentation}<{self.tag}{self._props_str()}{children_str}/>"


class TextNode(HtmlNode):
    def __init__(self, text: str, preserve_whitespace=False):
        if preserve_whitespace:
            text = text.replace("\t", HTML_WHITESPACE * config.mdparser.tabsize)
            text = text.replace(" ", HTML_WHITESPACE)
        
        self.tag = "text"
        self.children = []
        self.text: str = text
        self.properties = {}
        
    def __str__(self, depth=0): 
        text = ' ' * depth * config.document.indent_html + self.text
        return text

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

    def __str__(self):
        return self.create_document()

    def save(self, filepath: str):
        with open(filepath, 'w') as f:
            f.write(str(self))

    def create_document(self) -> str:
        style = "\n".join(try_read_file(style_path) for style_path in self.style_files)
        script = "\n".join(try_read_file(script_path) for script_path in self.script_files)
        
        return f"""
<!DOCTYPE html>
<html lang="{self.lang}">
    <head>
        <meta charset="{self.charset}">
        <title>{self.title}</title>
        <script src="https://cdn.jsdelivr.net/gh/google/code-prettify@master/loader/run_prettify.js?lang=css&amp;skin=default"></script>
        <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
        <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/clipboard.js/2.0.8/clipboard.min.js"></script>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/octicons/16.0.0/octicons.min.css">
        {self.head_str}
    </head>

{self.body}


    <style>
        {style}

        {self.style_str}
    </style>
    
    <script>
        {script}
        {self.script_str}
    </script>
    
  
</html>
"""