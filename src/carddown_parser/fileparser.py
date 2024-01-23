import random, json, re
from .mdparser import parse_markdown
from .mdparser.htmltree import  SelfClosingTag, HtmlNode, TextNode

from .mdparser.utils import get_hash, clean_string
from .cards import LearningCard
from .errors import try_read_file, show_warning_msg
from .config import get_config, get_locals

config = get_config()




class CardDeck:
    def __init__(self):
        self.cards: list[LearningCard] = []

    def add_card(self, card: LearningCard):
        self.cards.append(card)

    def to_json(self, filepath, include_styles=False):
        with open(filepath, "w") as f:
            f.write(json.dumps([c.to_dict(include_styles) for c in self.cards], indent=2, ensure_ascii=False))
    
    def shuffle(self):
        random.shuffle(self.cards)

    def get_cards_html(self):
        return [c.html for c in self.cards]
    
    def get_text_unparsed(self):
        return [(c.front, c.back) for c in self.cards]



class FileParser:

    def __init__(self):
        self.html: list[HtmlNode] = []
        self.cards = CardDeck()
  
        self.markdown = []


    def make_heading_ids(self, root_node: HtmlNode):
       
        hashes = {}
        
        headings = []
        
        for node in root_node:
            tag = node.tag
    
            if tag in [f"h{i}" for i in range(1,7)]:

                id = node.properties.get("id", node.get_inner_text())
                hash = get_hash(clean_string(id), max_length=8)
                
                if hash in hashes:
                    hashes[hash] += 1
                    hash += str(hashes[hash])
                else:
                    hashes[hash] = 0
                
                id = f"h-{hash}"
                node.properties["id"] = id

                headings.append(node)
        
        # The headings are stored for efficiency as they are needed to make the table of contents
        self.headings = headings
            
    

    def toc_list(self, items: list, parent: HtmlNode, last_lvl: int, start: int) -> int:
        i = start
        while i < len(items):
            lvl, li = items[i]
    
            if lvl > last_lvl:
                new_list = HtmlNode("ul", set_class="toc-ul")
                i = self.toc_list(items, new_list, lvl, i)
                parent.add_children(new_list)
            elif lvl == last_lvl:
                parent.add_children(li)
                i += 1
            else:
                return i      

        return i


    def toc_find_headings(self, max_lvl=3) -> list[tuple[int, HtmlNode]]:
        headings = {
                f"h{i}" : i 
                for i in range(1, max_lvl+1)
        }
        
        count = 0
        
        items = []
        last_non_card_heading_lvl = 0
    
        for node in self.headings:
            tag = node.tag
    
            if tag in headings:
    
                if in_card_back := any(node.search_parents_by_property(set_class="back")):
                    in_card = True
                else:
                    in_card = any(node.search_parents_by_property(set_class="card"))

                if in_card and not config.document.toc_include_cards:
                    continue

                heading_lvl = headings[tag]
        
                text = node.get_inner_text()
                
                if text.strip() == "" \
                        or (in_card_back and not config.document.toc_show_back_headings_cards) \
                        or (in_card and heading_lvl > config.document.toc_max_heading_cards):
                    continue
                
                
                href = f"#{node.properties['id']}"
                
                if in_card: 
                    if heading_lvl == 1:
                        text = f"{get_locals()['card']}: " + text
                    heading_lvl += last_non_card_heading_lvl
                else:
                    last_non_card_heading_lvl = heading_lvl
                
                a = HtmlNode("a", text, href=href, set_class="toc-link")
                li = HtmlNode("li", a)
                items.append((heading_lvl, li))
                count += 1
    
        return items


  
    def make_table_of_contents(self, max_lvl=3) -> list[HtmlNode]:
        
        items = self.toc_find_headings(max_lvl)
        if not items:
            return []
        
        uls = []
        
        i = 0
        count = 0
        
        while i < len(items) and count <= len(items):
            ul = HtmlNode("ul", set_class="toc-ul")
            i = self.toc_list(items, ul, items[i][0], i)
            uls.append(ul)
            count += 1
        
        if count > len(items):
            show_warning_msg("Something went wrong creating the table of contents")
            return []
        
        heading = HtmlNode("h1", get_locals()["toc"], HtmlNode("button", HtmlNode("i", set_class="fa-solid fa-chevron-up"), id="toc-btn"))
        content_div = HtmlNode("div", *uls, set_class="toc-content")
        return [HtmlNode("div", HtmlNode("span", heading),  content_div, set_class="toc")]


    def add_card(self, card_str):
        card = LearningCard.from_str(card_str)
        self.html.append(card.to_html())
        if tag := config.cardloader.card_separator:
            sep = SelfClosingTag(tag)
            card.html.add_children(sep)

        self.cards.add_card(card)


    def parse_card(self, lines: list[str], start: int):
        
        def check_length():
            if config.cardloader.length_warning and i - start >= config.cardloader.length_warning:
                print(f"Warning: Unusually long card detected (Line {start+1}-{i+1}). Did you maybe forget an {{END}} tag?")

        for i, line in enumerate(lines[start+1:], start+1):
            if line.rstrip() == LearningCard.end_tag:
                card_str = "".join(lines[start:i-1]) # dont include end tag
                self.add_card(card_str)
                return i + 1
            
            if LearningCard.is_card(line):
                check_length()
                card_str = "".join(lines[start:i])
                self.add_card(card_str)
                return i
        
        check_length()

        card_str = "".join(lines[start:])
        self.add_card(card_str)
        return i + 1
    


    def process_footnotes(self, cards_only=False) -> list[HtmlNode]:
        
        if cards_only:
            root_node = HtmlNode("root", *self.cards.get_cards_html())
        else:
            root_node = HtmlNode("root", *self.html)

        refs = root_node.search_by_property("set_class", "footnote-ref")
        footnote_divs = list(root_node.search_by_property("set_class", "footnotes-div"))
        

        for footnote_div in footnote_divs:
            footnote_div.remove_from_tree()

        div_container = HtmlNode("container", *footnote_divs)

        display_div = HtmlNode("div", set_class="footnotes-div")

        for count, fn_ref in enumerate(refs, 1):
            fn_text = fn_ref.properties["id"].replace("ref-", "")
           
            fn_ref.children[0].replace_in_tree(TextNode(f"[{count}]"))
            fn_id = f"footnote-{fn_text}"

            fn = next(div_container.search_by_property("id", fn_id, substring_search=False, find_all=False))
            fn_container = fn.parent.parent
            fn.children[0].replace_in_tree(f"{count}.")
            display_div.add_children(fn_container)

        if display_div.children:
            root_node.add_children(display_div)
      
        return root_node.children




    def get_cards(self, shuffle=False):
        if shuffle:
            self.cards.shuffle()

        cards_html = self.process_footnotes(cards_only=True)
        
        container = HtmlNode("container", *cards_html)
        self.make_heading_ids(container)

        if config.document.table_of_contents:
            config.document.toc_include_cards = True # If only cards are rendered and toc is True, not including the cards wouldn't make sense
            toc_div = self.make_table_of_contents(config.document.toc_max_heading)
            doc = toc_div + cards_html
            return doc
        
        return cards_html
    

    def get_markdown(self):
        return self.markdown


    def get_cards_and_markdown(self):
        self.html = self.process_footnotes()
        container = HtmlNode("container", *self.html)
        self.make_heading_ids(container)
      
        if config.document.table_of_contents:
            toc_div = self.make_table_of_contents(config.document.toc_max_heading)
            doc = toc_div + self.html 
            return doc
        
        return self.html
       
       

    def parse_file(self, input_file: str):
        
        lines = try_read_file(input_file)
        
        lines = lines.splitlines(True)

        i = 0
        md_string = ""

        while i < len(lines):
            line = lines[i]

            if LearningCard.is_card(line):
                md_elems = parse_markdown(md_string)
                self.markdown.extend(md_elems)
                self.html.extend(md_elems)
                md_string = ""
                i = self.parse_card(lines, i)
            else:
                md_string += line
                i += 1

        md_elems = parse_markdown(md_string)
        self.html.extend(md_elems)
        self.markdown.extend(md_elems)

