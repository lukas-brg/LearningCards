import re, traceback
from typing import Callable


from .tokens import InlineToken, LinkToken
from .latex import latex_to_svg
from .htmltree import HtmlNode, SelfClosingTag, WhiteSpaceNode, TextNode
from .utils import leading_whitespaces, multiline_strip, find_line, make_id_hash
from .escape_sequences import ESCAPE_SEQUENCES, escape_text, unescape_text_in_tree
from ..errors import try_read_file, MarkdownSyntaxError, show_warning_msg
from ..config import get_config, ENABLE_DEBUG
from ..config import get_locals

config = get_config()


ORDERED_LIST_PATTERN = r"^\d+\. "

HEADINGS = {
    '#'     : 'h1',
    '##'    : 'h2',
    '###'   : 'h3',
    '####'  : 'h4',
    '#####' : 'h5',
    '######': 'h6'
}


HEADING_PATTERN = r"^#{1,6} "

MULTILINE_CODE = "```"

TABLE_PATTERN = r"^\s*\|(\s*\S+.*)\|"

DEF_PATTERN = r"^: \S+"

FOOTNOTE_PATTERN = r"^\[\^(\S+)\]:()"
    
HEADING_ID_PATTERN = r"\{#(\S+)\}"

CHECKED_PATTERN = "- [x]"
UNCHECKED_PATTERN = "- [ ]"


HTML_PATTERN = r"<([a-zA-Z0-9-]+)([^>/]*?)\s*/>|<([a-zA-Z0-9-]+)([^>]*)>(.*?)<\/\3>"


is_ul       = lambda line : line.strip().startswith(tuple((list_token + ' ' for list_token in config.mdparser.list_item_chars)))
is_ol       = lambda line : re.search(ORDERED_LIST_PATTERN, line.strip())
is_dd       = lambda line : re.search(DEF_PATTERN, line)
is_hr       = lambda line : re.match(r"[*]{3,}|[-]{3,}", line.replace(" ", ""))
is_list     = lambda line : is_ul(line) or is_ol(line) 
is_table    = lambda line : re.search(TABLE_PATTERN, line)
is_latex    = lambda line : line.startswith("$$")
is_heading  = lambda line : re.search(HEADING_PATTERN, line)

is_checked      = lambda line : line.startswith(CHECKED_PATTERN)
is_footnote     = lambda line : re.search(FOOTNOTE_PATTERN, line)
is_unchecked    = lambda line : line.startswith(UNCHECKED_PATTERN)
is_task_list    = lambda line : is_checked(line) or is_unchecked(line)
is_block_quote  = lambda line : line.lstrip().startswith(">")

is_codeblock_fenced   = lambda line : re.match(r"^```\s*(\S*)$", line.rstrip())
is_codeblock_indented = lambda line : leading_whitespaces(line) >= 4 or line.strip() == "" or line.startswith("\t")


token_types = None



def get_token_types() -> list[InlineToken]:
    """Make sure list of TokenTypes to be parsed is only computed once for efficiency"""
    global token_types
    if not token_types:
        token_types = [TokenType for TokenType in InlineToken.get_all_token_types() if TokenType.__name__ not in config.mdparser.ignore_inline_tokens]
    return token_types
    

def get_heading_node(heading_marker: str) -> HtmlNode:
    return HtmlNode(HEADINGS[heading_marker])


def is_def(lines: list[str], i: int) -> bool:
    return not is_dd(lines[i]) and i < len(lines) - 1 and is_dd(lines[i+1])


def get_list_tag(line: str) -> str: 
    if not is_list(line):
        return None
    return "ul" if is_ul(line) else "ol"



def find_tokens(line: str) -> dict[int, InlineToken]:
    """Returns a dict containing all the tokens in a single line, 
        where the key is the start index of the token.
    """
    tokens = {}


    for TokenType in get_token_types():
        for pattern in TokenType.patterns:
            matches = re.finditer(pattern, line)
            for match in matches:
                token = TokenType.create(match)
                tokens[token.start] = token

    return tokens


def parse_link(line: str, start: int) -> HtmlNode:
    bracket_count = 1
    paren_count = 0
    for i, char in enumerate(line[start+1:], start+1):
        if char == "]":
            bracket_count -= 1
        elif char == "[":
            bracket_count += 1
        if bracket_count == 0:
            break
    content_end = i

    for i, char in enumerate(line[content_end+1:], content_end+1):
        if char == "(":
            paren_count += 1
        elif char == ")":
            paren_count -= 1
        if paren_count == 0:
            break
    
    link_end = i+1
    content = line[start+1:content_end]
    content_elems = parse_inline(content)
    link_contentless = line[start:start+1] + line[content_end:link_end]

    link_match = re.match(LinkToken.patterns[0], link_contentless)
    link_elem = LinkToken.create(link_match).to_html()
    link_elem.set_children(content_elems)
    return link_elem, link_end


def _parse_inline(line: str, tokens: dict[int, InlineToken], parent: HtmlNode, start: int, end: int, parse_content=True):

    i = start
    text = ""

    while i < end:
        
        if i in tokens and parse_content:
            
            parent.add_children(text)
            text = ""
            token = tokens[i]
            
            if isinstance(token, LinkToken):
                html_elem, i = parse_link(line, i)
            else:
                html_elem = token.to_html()
                _parse_inline(line, tokens, html_elem, token.content_start, token.content_end, token.parse_content)
                i = token.end
            parent.add_children(html_elem)
        else:
            text += line[i]
            i += 1

    parent.add_children(text)


def parse_inline(line: str) -> list[HtmlNode]:
    
    tokens = find_tokens(line)
    temp_container = HtmlNode("container")
    
    if not tokens:
        temp_container.add_children(line)
    else:
        _parse_inline(line, tokens=tokens, parent=temp_container, start=0, end=len(line))

    return temp_container.children



def handle_tasklist_item(line: str, parent: HtmlNode):
    hash = make_id_hash(line, limit_len=8)
    id=f"task_list_checkbox-{hash}" 
    line = line.strip()
    
    check_box = SelfClosingTag("input", type="checkbox", id=id, autocomplete="off")
    if is_checked(line):
        line = line.replace(CHECKED_PATTERN, "").strip()
        check_box.boolean_attributes.add("checked")
        
    else:
        line = line.replace(UNCHECKED_PATTERN, "").strip()
    
    if config.mdparser.checkbox_disabled:
        check_box.attributes["disabled"] = "disabled"
    
    line = parse_inline(line)
    label = HtmlNode("label", *line, set_for=id)
    parent.add_children(check_box, label, SelfClosingTag("br"))



def _parse_list(lines: list[str], start: int, prev_spaces: int, parent: HtmlNode, prev_tag: str):
    i = start
    while i < len(lines):
        line = lines[i]
        
        if not line.strip():
            i += 1
            continue
        
        line_spaces = leading_whitespaces(line)
        line_tag = get_list_tag(line)
        
        # new list on same level starts
        if line_tag != prev_tag and line_spaces == prev_spaces:
            return i
        
        # list on current level ends
        if not is_list(line) or line_spaces < prev_spaces:
            return i

        # new sublist starts
        if line_spaces > prev_spaces:
            sublist, i = parse_list(lines, i)
            parent.add_children(sublist)
            
        # list item
        else: 
            if is_task_list(line.strip()):
                handle_tasklist_item(line, parent=parent)
            else:
                _, li_text = line.strip().split(" ", 1)
                inline_elems = parse_inline(li_text.strip())
                parent.add_children(HtmlNode('li', *inline_elems))
            i += 1

    return i



def parse_list(lines: list[str], start: int) -> tuple[HtmlNode, int]:
    tag = get_list_tag(lines[start])
    
    if tag == "ol":
        list_start, _ = lines[start].strip().split(".", 1)
        list = HtmlNode("ol", start=list_start)
    else:
        list = HtmlNode("ul")
        
    spaces = leading_whitespaces(lines[start])
  
    end = _parse_list(lines, start, spaces, list, tag)
    return list, end



def make_codeblock_elem(code_lines: list[str], lang: str):
    name="multiline-code-block"
    if config.mdparser.prettyprint_multiline_code or lang != "":
        lang_str = f" lang-{lang}" if lang else ""
        code = HtmlNode("code", set_class=f"code-block prettyprint{lang_str}")
    else:
        code = HtmlNode("code", name=name, set_class="code-block")
    code_str = "\n".join(code_lines)
    code_str = code_str.replace("<", "&lt;")
    code_str = code_str.replace(">", "&gt;")
    code.add_children(code_str) 

    id_hash = make_id_hash(code.get_inner_text(), limit_len=8)

    code.attributes["id"] = "code-block_" + id_hash
    code_container = HtmlNode("div", HtmlNode("pre", code), set_class="code-block-container")
    scrollbar_container = HtmlNode("div", code_container, set_class="code-block-scrollbar-container")
    
    if config.document.codeblock_copy_btn is False:
        return HtmlNode(
            "div",
            scrollbar_container,
            id=f"code-div_{id_hash}", 
            set_class="multiline"
        )
    
    # The btn text is supposed to get replaced by an icon in js
    copy_btn = HtmlNode("button", "Copy", set_class="btn-copy", id=f"copy-button_{id_hash}")
    copy_btn.attributes["data-clipboard-target"] = f"#{code.attributes['id']}"
    copy_notification = HtmlNode("div", get_locals()["copied"], set_class="copy-notification", id=f"copy-notification_{id_hash}")
    code_div = HtmlNode(
            	    "div", 
                    scrollbar_container,
                    copy_notification, 
                    copy_btn,
                    id=f"code-div_{id_hash}", 
                    set_class="multiline"
    )

    return code_div


def parse_codeblock_fenced(lines: list[str], start: int) -> tuple[HtmlNode, int]:
    lang = lines[start].strip().replace("```", "")
    end = find_line(lines, start+1, function=is_codeblock_fenced)
    code_lines =  multiline_strip(lines[start+1:end])
    
    if end == len(lines):
        show_warning_msg(f"Unclosed multiline code detected. (line {start+1}-{end})")
    
    code_div = make_codeblock_elem(code_lines, lang)
   
    return code_div, end+1


def parse_codeblock_indented(lines: list[str], start: int) -> tuple[HtmlNode, int]:
    remove_indentation = lambda line : re.sub(r"^(\t|\s{4})", "", line)
    
    end = find_line(lines, start+1, function=is_codeblock_indented, negate=True)
    code_lines =  [remove_indentation(line) for line in multiline_strip(lines[start:end])]
    
    if end == len(lines):
        show_warning_msg(f"Unclosed multiline code detected. (line {start+1}-{end})")
    
    code_div = make_codeblock_elem(code_lines, lang="")
   
    return code_div, end

    

def get_alignments(header: str) -> list[dict[str, str]]:
    table_head_separator_pattern = r"^(\|[:\-\s]+)+"
    table_cols_pattern = r"\|([^\|\n]+)"

    if not re.search(table_head_separator_pattern, header):
        raise MarkdownSyntaxError("No Table header!")
    
    cols = re.findall(table_cols_pattern, header)
    alignments = []

    default = {"style" : f"text-align:{config.mdparser.table_align}"}

    for col in cols:
        col = col.strip()
        if len(col) <= 2:
            alignments.append(default)
        elif col[0] == ":" and col[-1] == ":":
            alignments.append({"style" : "text-align:center"})
        elif col[0] == ":":
            alignments.append({"style" : "text-align:left"})
        elif col[-1] == ":":
            alignments.append({"style" : "text-align:right"})
        else:
            alignments.append(default)

    return alignments


def parse_table(lines: list[str], start: int) -> tuple[HtmlNode, int]:
    table = HtmlNode("table")
    head = HtmlNode("thead")
    top_row = HtmlNode("tr")
    table_cols_pattern = r"\|([^\|\n]+)"
   
    alignments = get_alignments(lines[start+1])
    top_row_matches = re.findall(table_cols_pattern, lines[start])
    top_row_cols = [
        HtmlNode("th", HtmlNode("b", *parse_inline(col.strip())), **align) 
        for col, align in zip(top_row_matches, alignments)
    ]
    
    
    top_row.add_children(*top_row_cols)
    head.add_children(top_row)
    table.add_children(head)    
    
    num_cols = len(top_row_cols)

    tbody = HtmlNode("tbody")
    i = start + 2
    for i, line in enumerate(lines[start+2:], start+2):
        if not is_table(line):
            break
        tr = HtmlNode("tr")
        row_matches = re.findall(table_cols_pattern, line)
        
        if len(row_matches) != num_cols:
            raise MarkdownSyntaxError(f"Inconsistent number of columns in table.\n'{line}'")

        cols = [
                HtmlNode("td", *parse_inline(col.strip()), **align) 
                for col, align in zip(row_matches, alignments)
        ]
        
        tr.add_children(*cols)
        tbody.add_children(tr)
  
        
    table.add_children(tbody)

    for node in table:
        if isinstance(node, TextNode):
            node.text = node.text.replace(ESCAPE_SEQUENCES["\|"]["intermediate"], "|")

    end = len(lines) if i >= len(lines) - 1 else i 
    return table, end


def parse_def(lines: list[str], start: int) -> tuple[HtmlNode, int]:
   
    dl = HtmlNode("dl")
    i = start
    for i, line in enumerate(lines[start:], start):
    
        if line.strip() == "":
            i += 1
            dl.add_children(SelfClosingTag("br"))
            continue

        if not is_dd(line):
            if i >= len(lines) - 2:
                break
            elif is_dd(lines[i+1]):
                inline_elems = parse_inline(line)
                dt = HtmlNode("dt", *inline_elems)
                dl.add_children(HtmlNode("b", dt))
            else:
                break
        else:
            inline_elems = parse_inline(line.lstrip(": "))
            dd = HtmlNode("dd", *inline_elems)
            dl.add_children(dd)
    
    end = len(lines) if i >= len(lines) - 1 else i 
    
    return dl, end


def parse_heading(line: str) -> HtmlNode:
    h, line = line.split(' ', 1)
    heading = get_heading_node(h)
    
    if id_match := re.search(HEADING_ID_PATTERN, line):
        id = id_match.group(1)
        heading.attributes["id"] = id
        line = re.sub(HEADING_ID_PATTERN, "", line)

    inline_elems = parse_inline(line)
    heading.add_children(*inline_elems)
    return heading


def get_blockquote_depth(line: str) -> int:
    return len(line.strip()) - len(line.strip().lstrip(">"))


def parse_blockquote(lines: list[str], start: int, depth=1) -> tuple[HtmlNode, int]:
    blockquote = HtmlNode("blockquote")
    i = start
    text = ""
    
    while i < len(lines):
        
        line = lines[i]
        line_depth = get_blockquote_depth(line)
        if not is_block_quote(line) or line_depth < depth:
            break
        if line_depth > depth:
            new_quote, i = parse_blockquote(lines, i, line_depth)
            paragraph = HtmlNode("p", *parse_markdown(text, paragraph=False))
            blockquote.add_children(paragraph, new_quote)
            text = ""
        else:
            line = line.lstrip("> ")
            text += line + "\n"
            i += 1
    
    if text.strip():
        blockquote.add_children(HtmlNode("p", *parse_markdown(text, paragraph=False)))
    
    return blockquote, i




def parse_footnotes(lines: list[str], start: int) -> tuple[HtmlNode, int]:
    footnotes_div = HtmlNode("div", set_class="footnotes-div")
    footnote_div = HtmlNode("div", set_class="footnote")
    footnote_links = []
   
    for i, line in enumerate(lines[start:], start):
     
        if line.strip() == "":
            continue

        if (leading_whitespaces(line)) >= 2:
            inline_elems = [WhiteSpaceNode(3), *parse_inline(line)]
        
        elif match := re.search(FOOTNOTE_PATTERN, line):
            
            if footnote_div.children:
                footnotes_div.add_children(footnote_div)

            
            footnote_div = HtmlNode("div", set_class="footnote")
            
            text = match.group(1).strip()
            href = f"#ref-{text}"
            id = f"footnote-{text}"
            text += ":"
            
            a = HtmlNode("a", " &#8617;", href=href)
            
            footnote_links.append(a)
     
            footnote = HtmlNode("span", text,  id=id)
            
            line = re.sub(FOOTNOTE_PATTERN, "", line)
            inline_elems = [footnote, *parse_inline(line)]
                        
        else:
            break
            
        p = HtmlNode("p", *inline_elems, set_class="footnote-paragraph")
        footnote_div.add_children(p)

    end = len(lines) if i >= len(lines) - 1 else i 
    
    if footnote_div.children:
        footnotes_div.add_children(footnote_div)
    
    # Make link to footnote ref always be at the end of the footnote
    for fn, a in zip(footnotes_div.children, footnote_links):
        fn.children[-1].add_children(a)

    return footnotes_div, end


def append_paragraph(elems: list[HtmlNode], p: HtmlNode, use_paragraph: bool) -> HtmlNode:
    """Convenience function that adds the current paragraph to the list of parsed HtmlNodes 
        and returns an empty paragraph object to avoid repetition"""
    if use_paragraph and p.contains_text():       
        elems.append(p)
    else:
        elems.extend(p.children)

    return HtmlNode("p")


                         
def parse_blockrule(parse_func: Callable, start: int, lines: list[str], **kwargs) -> tuple[HtmlNode, int]:
    """ 
    Errors that occur while parsing blockrules are handled by this wrapper function to avoid repetition. 
    In the error case the plain text is displayed and a warning message is issued 
    """
    
    try:
        node, end = parse_func(start=start, lines=lines, **kwargs)
        return node, end
    except Exception as e:
        if ENABLE_DEBUG:
            traceback.print_exc()
        print(f"Warning: Failed to parse blockrule '{parse_func.__name__.replace('parse_', '')}'. {type(e).__name__}: {e}")
        return HtmlNode("span",  SelfClosingTag("br"), TextNode(lines[start], preserve_whitespace=True)), start+1



def parse_latex(lines: list[str], start: int) -> HtmlNode:
    lines[start] = lines[start][2:]
    latex_str = ""
    for i, line in enumerate(lines[start:], start):
        line = line.strip()
        latex_str += line
        if line.endswith("$$"):
            latex_str = latex_str[:-2]
            break

    backslash_esc = ESCAPE_SEQUENCES[r"\\"]
    latex_str = latex_str.replace(backslash_esc["intermediate"], r"\\")
    if config.document.prerender_latex:
        latex_str = latex_str.replace(" ", "")
        svg_data = latex_to_svg(latex_code=latex_str)
        node = HtmlNode("div", svg_data, set_class="latex block-latex")
    else:
        latex_str = latex_str.replace("<", "&lt;").replace(">", "&gt;")
        node = HtmlNode("div", "$$" + latex_str + "$$", set_class="latex block-latex")
    
    end = len(lines) if i+1 >= len(lines) - 1 else i+1

    return node, end


def parse_markdown(markdown: list[str]|str, paragraph=True, add_linebreak=True) -> list[HtmlNode]:
    
    if isinstance(markdown, str):
        markdown = escape_text(markdown)
        lines = markdown.splitlines(False)
    else:
        lines = [escape_text(line) for line in markdown]


    parsed_elems = []
    i = 0
    p = HtmlNode("p")
    
    while i < len(lines):
        line = lines[i].rstrip()
        
        if line.strip() == "":
            if not config.mdparser.ignore_empty_lines:
                parsed_elems.append(SelfClosingTag("br"))
            p = append_paragraph(parsed_elems, p, paragraph)
            i += 1
            continue
        if line.rstrip() == "{\\newpage}":
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(HtmlNode("div", set_class="newpage"))
            i += 1
            continue
        
        if re.match(r"^<.+>$", line.strip()):
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(line)
            i += 1
        
        elif is_heading(line):  # Heading
            heading = parse_heading(line)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(heading)
            i += 1

        elif is_latex(line):
            latex, i = parse_blockrule(parse_func=parse_latex, lines=lines, start=i)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(latex)

        elif is_codeblock_indented(line):
            code, i = parse_blockrule(parse_func=parse_codeblock_indented, lines=lines, start=i)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(code)
       
        elif is_codeblock_fenced(line):
            code, i = parse_blockrule(parse_func=parse_codeblock_fenced, lines=lines, start=i)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(code)
        
        elif is_hr(line):
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(SelfClosingTag("hr"))
            i += 1
        
        elif is_list(line): # List
            list, i = parse_blockrule(parse_func=parse_list, lines=lines, start=i)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(list)
        
        elif is_table(line):
            table, i = parse_blockrule(parse_func=parse_table, lines=lines, start=i)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(table)
        
        elif is_def(lines, i):
            dl, i = parse_blockrule(parse_func=parse_def, lines=lines, start=i)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(dl)

        elif is_block_quote(line):
            quote, i = parse_blockrule(parse_func=parse_blockquote, lines=lines, start=i, depth=get_blockquote_depth(line))
            div = HtmlNode("div", quote, set_class="blockquote-div")
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(div)
        
        elif is_footnote(line):
            footnote_div, i = parse_blockrule(parse_func=parse_footnotes, lines=lines, start=i)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(footnote_div)

        else:                           # Text
            inline_elems = parse_inline(line) 
            if paragraph:
                p.add_children(*inline_elems, SelfClosingTag("br"))  
            else:
                if add_linebreak:
                    parsed_elems.extend([*inline_elems, SelfClosingTag("br")])
                else:
                    parsed_elems.extend(inline_elems)
            i += 1

    _ = append_paragraph(parsed_elems, p, paragraph)
    container = HtmlNode("container", *parsed_elems)
    unescape_text_in_tree(container)
    return container.detach_children()
   


def parse_markdown_file(filepath: str) -> list[HtmlNode]:
    markdown = try_read_file(filepath).splitlines(False)
    return parse_markdown(markdown)