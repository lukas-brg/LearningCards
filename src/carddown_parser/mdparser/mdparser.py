import re, traceback
from typing import Callable


from ..config import get_config, ENABLE_DEBUG
from .tokens import InlineToken
from .htmltree import HtmlNode, SelfClosingTag, WhiteSpaceNode, TextNode
from ..errors import try_read_file, MarkdownSyntaxError, show_warning_msg
from .utils import leading_whitespaces, multiline_strip, find_line, make_id_hash
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


is_ul       = lambda string : string.strip().startswith(tuple((list_token + ' ' for list_token in config.mdparser.list_item_chars)))
is_ol       = lambda string : re.search(ORDERED_LIST_PATTERN, string.strip())
is_dd       = lambda string : re.search(DEF_PATTERN, string)
is_list     = lambda string : is_ul(string) or is_ol(string) 
is_table    = lambda string : re.search(TABLE_PATTERN, string)
is_heading  = lambda string : re.search(HEADING_PATTERN, string)

is_checked      = lambda line : line.startswith(CHECKED_PATTERN)
is_footnote     = lambda line : re.search(FOOTNOTE_PATTERN, line)
is_unchecked    = lambda line : line.startswith(UNCHECKED_PATTERN)
is_task_list    = lambda line : is_checked(line) or is_unchecked(line)
is_block_quote  = lambda line : line.lstrip().startswith(">")

is_codeblock_fenced   = lambda string : re.match(r"^```\s*(\S*)$", string.rstrip())
is_codeblock_indented = lambda string : leading_whitespaces(string) >= 4 or string.strip() == ""
in_codeblock_indented = lambda string : leading_whitespaces(string) == 4


get_heading_elem    = lambda h      : HtmlNode(HEADINGS[h])


token_types = None


def get_token_types() -> list[InlineToken]:
    """Make sure list of TokenTypes to be parsed is only computed once for efficiency"""
    global token_types
    if not token_types:
        token_types = [TokenType for TokenType in InlineToken.get_all_token_types() if TokenType.__name__ not in config.mdparser.ignore_inline_tokens]
    return token_types
    


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
                if token.start == 0 or line[token.start-1] != "\\":
                    tokens[token.start] = token

    return tokens


def _parse_inline(line: str, tokens: dict[int, InlineToken], parent: HtmlNode, start: int, end: int, parse_content=True):

    i = start
    text = ""

    while i < end:
        
        if i in tokens and parse_content:
        
            parent.add_children(text)
            text = ""
            token = tokens[i]
            elem = token.to_html()
            
            _parse_inline(line, tokens, elem, token.content_start, token.content_end, token.parse_content)
            parent.add_children(elem)
          
            i = token.end
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
    
    if is_checked(line):
        check_box = SelfClosingTag("input", "checked", type="checkbox", id=id, autocomplete="off")
        line = line.replace(CHECKED_PATTERN, "").strip()
        
    else:
        check_box = SelfClosingTag("input", type="checkbox", id=id, autocomplete="off")
        line = line.replace(UNCHECKED_PATTERN, "").strip()
    
    if config.mdparser.checkbox_disabled:
        check_box.properties["disabled"] = "disabled"
    
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



def make_code_block_elem(code_lines: list[str], lang: str):
    name="multiline-code-block"
    if config.mdparser.prettyprint_multiline_code or lang != "":
        lang_str = f" lang-{lang}" if lang else ""
        code = HtmlNode("code", set_class=f"prettyprint{lang_str}", name=name)
    else:
        code = HtmlNode("code", name=name)

    code.add_children("\n".join(code_lines)) 

    id_hash = make_id_hash(code.get_inner_text(), limit_len=8)

    code.properties["id"] = "code-block_" + id_hash
    
    
    # The btn text is supposed to get replaced by an icon in js
    copy_btn = HtmlNode("button", "Copy", set_class="btn-copy", id=f"copy-button_{id_hash}")
    copy_btn.properties["data-clipboard-target"] = f"#{code.properties['id']}"
    copy_notification = HtmlNode("div", get_locals()["copied"], set_class="copy-notification", id=f"copy-notification_{id_hash}")
    code_container = HtmlNode("div", HtmlNode("pre", code), set_class="code-block-container")
    code_div = HtmlNode(
            	    "div", 
                    code_container,
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
    
    code_div = make_code_block_elem(code_lines, lang)
   
    return code_div, end+1


def parse_codeblock_indented(lines: list[str], start: int) -> tuple[HtmlNode, int]:
  
    end = find_line(lines, start+1, function=is_codeblock_indented, negate=True)
    code_lines =  [line.strip() for line in multiline_strip(lines[start:end])]
    
    if end == len(lines):
        show_warning_msg(f"Unclosed multiline code detected. (line {start+1}-{end})")
    
    code_div = make_code_block_elem(code_lines, lang="")
   
    return code_div, end

    

def get_alignments(header: str) -> list[dict[str, str]]:
    table_head_separator_pattern = r"^(\|[-\s]+)+"
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
            raise MarkdownSyntaxError("Inconsistent number of columns in table.")

        cols = [
                HtmlNode("td", *parse_inline(col.strip()), **align) 
                for col, align in zip(row_matches, alignments)
        ]
        
        tr.add_children(*cols)
        tbody.add_children(tr)
  
    
    table.add_children(tbody)
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
    heading = get_heading_elem(h)
    
    if id_match := re.search(HEADING_ID_PATTERN, line):
        id = id_match.group(1)
        heading.properties["id"] = id
        line = re.sub(HEADING_ID_PATTERN, "", line)

    inline_elems = parse_inline(line)
    heading.add_children(*inline_elems)
    return heading


def get_blockquote_depth(line: str) -> int:
    return len(line.strip()) - len(line.strip().lstrip(">"))


def parse_block_quote(lines: list[str], start: int, depth=1) -> tuple[HtmlNode, int]:
    blockquote = HtmlNode("blockquote")
    i = start
    text = ""
    
    while i < len(lines):
        
        line = lines[i]
        line_depth = get_blockquote_depth(line)
        if not is_block_quote(line) or line_depth < depth:
            break
        if line_depth > depth:
            new_quote, i = parse_block_quote(lines, i, line_depth)
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



def parse_markdown(markdown: list[str]|str, paragraph=True, add_linebreak=True) -> list[HtmlNode]:
    
    if isinstance(markdown, str):
        lines = markdown.splitlines(False)
    else:
        lines = markdown

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
        
        if is_heading(line):  # Heading
            heading = parse_heading(line)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(heading)
            i += 1

        elif is_codeblock_fenced(line):
            code, i = parse_blockrule(parse_func=parse_codeblock_fenced, lines=lines, start=i)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(code)
            
        elif is_codeblock_indented(line):
            code, i = parse_blockrule(parse_func=parse_codeblock_indented, lines=lines, start=i)
            p = append_paragraph(parsed_elems, p, paragraph)
            parsed_elems.append(code)
        
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
            quote, i = parse_blockrule(parse_func=parse_block_quote, lines=lines, start=i, depth=get_blockquote_depth(line))
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
    
    return parsed_elems
   


def parse_markdown_file(filepath: str) -> list[HtmlNode]:
    markdown = try_read_file(filepath).splitlines(False)
    return parse_markdown(markdown)