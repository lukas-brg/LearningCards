from __future__ import annotations

import re

from abc import ABC
from functools import lru_cache
from .mdparser.htmltree import HtmlNode, SelfClosingTag
from .mdparser import parse_markdown
from .mdparser.utils import find_subclasses, make_id_hash
from .errors import CardSyntaxError
from .config import get_config, get_local, get_locals


config = get_config()


class LearningCard(ABC):
    start_tag: str
    split_pattern: str
    
    replace_patterns = ["{BACK}"]
    end_tag = "{END}"
   
    collapse = True
    card_count = 0 

    __card_types: list[type[LearningCard]]|None = None


    def __init__(self, front: str, back: str):
        self.front = front
        self.back = back
        self.not_collapse = False
        self.id = LearningCard.card_count
        LearningCard.card_count += 1
        self.start = 0 # line number where the card starts. used to display line numbers in error messages correctly
        self.replace_patterns.append(self.start_tag)
            
        for pattern in self.replace_patterns:
            self.front = self.front.replace(pattern, "")
            self.back = self.back.replace(pattern, "")
        
        self.validate_format()

    
    def validate_format(self):
        if self.back.strip() == "":
            raise CardSyntaxError(f"Empty backside on card {self.id+1}: \n" + self.front)


    def to_dict(self, include_styles=False):
        
        front = self.front if include_styles else self.front_div.get_inner_text()
        back = self.back if include_styles else self.answer_div.get_inner_text()
        
        return {
            "type"  : type(self).__name__,
            "front" : front,
            "back"  : back
        }


    def parse_backside(self, back_str: str) -> list[HtmlNode]:
       return parse_markdown(back_str)


    def generate_collapsible_backside(self, *content: HtmlNode|str, parent: HtmlNode):
      
        if not config.cardloader.collapse or self.not_collapse:
            parent.add_children(*content)
            return                  
        
        btn = HtmlNode("button", get_locals()["show_backside"], set_class="collapsible card-btn")
        content = HtmlNode("div", *content, set_class="content")
        parent.add_children(btn, content, SelfClosingTag('br'))


    def to_html(self) -> HtmlNode:
        card_type_name = type(self).__name__
        self.collapsible = config.cardloader.collapse
        front_elems = parse_markdown(self.front)    
        front_div = HtmlNode("div", *front_elems, set_class=f"front {card_type_name}")
        self.front_div = front_div
       
        back_elems = self.parse_backside(self.back)
        answer = HtmlNode("div", *back_elems, set_class="answer")
        back_div = HtmlNode("div", set_class=f"back {card_type_name}")
        
        self.generate_collapsible_backside(answer, parent=back_div)
        
        self.back_div = back_div # Whole backside, including collapse button etc.
        self.answer_div = answer # Only user written text
        
        card_div = HtmlNode("div", front_div, back_div, set_class=f"card {card_type_name}", id=self.id)
        self.html: HtmlNode = card_div
        
        return card_div


    @staticmethod
    def get_all_card_types():
        if not LearningCard.__card_types:
            LearningCard.__card_types = find_subclasses(LearningCard)
        return LearningCard.__card_types


    @staticmethod
    def get_card_type(string) -> type[LearningCard] | None:
        """Returns class of matching LearningCard Type if any"""
        for CardType in LearningCard.get_all_card_types():
            
            if CardType.matches(string):
                return CardType
        return None


    @staticmethod 
    def is_card(string) -> bool:
        """Checks if a string matches with any LearningCard Type"""
        return LearningCard.get_card_type(string) is not None


    @classmethod
    def split(CardType, string: str):
        return re.split(CardType.split_pattern, string)


    @classmethod
    def matches(CardType, string: str) -> bool:
        first_line, *_ = string.split("\n", 1)
        return first_line.startswith('# ') and CardType.start_tag in first_line
    

    @staticmethod 
    def from_str(string):
        """Takes a string and returns an instance of the matching LearningCard Type"""
        CardType = LearningCard.get_card_type(string)
        if not CardType:
            return None
        return CardType.parse(string)

    @classmethod
    def parse(CardType, string):    
        """This method extracts the front and backside out of the card string and creates an instance"""
        split = CardType.split(string)
        front, back = split
      
        return CardType(front, back)


    def __str__(self):
        return f"front:\n{self.front}\nback:\n{self.back}\n"



class QuestionCard(LearningCard):
        start_tag = '{CARD}'
        #split_pattern = r"(## .*\{BACK\}.*)"
        split_pattern = r"\{BACK\}"

        @classmethod
        def parse(QuestionCard, string):
            split_card = QuestionCard.split(string)
            if len(split_card) == 1: # In Case the card doesnt have a {BACK} Tag
                lines = string.splitlines(True)
                front = lines[0]
                back = "".join(lines[1:])
            else:
                front, back = split_card
            return QuestionCard(front, back)



class AnswerCard(QuestionCard):
    start_tag = '{ANSWER}'
    answer_pattern = r"{(\S.*)}"
    collapse = False

    def parse_backside(self, back_str: str) -> list[HtmlNode]:
        answer_match = re.search(AnswerCard.answer_pattern, back_str)
        self.not_collapse = True        
        
        if not answer_match:
            answer = back_str
            answer_start = 0
            answer_end = len(answer)
        else:
            answer = answer_match.group(1)
            answer_start, answer_end = answer_match.span()


        pre_answer = back_str[:answer_start]
        post_answer = back_str[answer_end:]
        
        # pre_answer_html = parse_markdown(pre_answer)
        # post_answer_html = parse_markdown(post_answer)
        pre_answer_html = parse_markdown(pre_answer, paragraph=pre_answer[-1]=='\n', add_linebreak=False) if pre_answer else []
        post_answer_html = parse_markdown(post_answer, paragraph=post_answer[0]=='\n', add_linebreak=False) if post_answer else []
        input = SelfClosingTag("input", type="text", set_class="answer-input", name=f"answer_field{self.id}", autocomplete="off")
        answer_span = HtmlNode("span", answer, name=f"answer{self.id}", set_class="answer-span")
        
        btn = SelfClosingTag(
                "input", 
                value=get_local("check_answer"),  
                type="submit", 
                set_class="answer-btn card-btn", 
                id=f"answer_btn{self.id}", 
                onclick=f"answerOnClick(this)"
        )

        form = HtmlNode("form", input, SelfClosingTag("br"), btn, action=f"javascript:void(0);")
        
        answer_div = HtmlNode("div", set_class="answer-content", name=f"answer_content{self.id}")
        answer_div.add_children(HtmlNode("p", *pre_answer_html, answer_span, *post_answer_html))

        if config.cardloader.collapse:
            return [form, answer_div]
        else:
            return [HtmlNode("div", *pre_answer_html, answer_span, *post_answer_html)]


class MultipleChoiceCard(QuestionCard):
    start_tag = '{MULTI}'
    multi_correct = "- [x] "
    mult_incorrect = "- [ ] "
    is_multi_correct = lambda string : string.startswith(MultipleChoiceCard.multi_correct)
    is_multi_incorrect = lambda string : string.startswith(MultipleChoiceCard.mult_incorrect)

    is_multi = lambda string : MultipleChoiceCard.is_multi_correct(string) or MultipleChoiceCard.is_multi_incorrect(string)
    

    def parse_multi(self, lines: list[str], start: int):
        
        multi_div = HtmlNode("form", set_class="multi", name=f"multiform{self.id}", action=f"javascript:void(0)")
        
        for i, line in enumerate(lines[start:], start):
            
            if line.strip() == "":
                start += 1
                continue
            
            choice_id = self.id + (i - start)
            
            if not MultipleChoiceCard.is_multi(line):
                break
            elif MultipleChoiceCard.is_multi_incorrect(line):
                line = line.replace(self.mult_incorrect, "")
                value = "incorrect"
            else:
                line = line.replace(self.multi_correct, "")
                value = "correct"
            
            id = f"choice_{make_id_hash(line, limit_len=8)}"
            
            choice = SelfClosingTag(
                    "input",
                    set_class="choice",
                    type="checkbox", 
                    id=id,
                    value=value, 
                    autocomplete="off"
            )
            
            inline_elems = parse_markdown(line, paragraph=False)
            label = HtmlNode("label", *inline_elems, name="label", set_for=id)
            multi_div.add_children(choice, label)
        
        submit = SelfClosingTag(
                "input",  
                value=get_local("check_answer"), 
                id=f"multi_btn{self.id}", 
                type="submit", 
                set_class="multi-btn card-btn", 
                onclick=f"multiOnClick(this)"
        )
       
        multi_div.add_children(SelfClosingTag("br"), submit)
        
        # parse everything that comes after choices
        post_elems = parse_markdown("".join(lines[i:])) if i < len(lines) - 1 else ""
        
        content_div = HtmlNode("div", *post_elems, set_class="multicontent")
        multi_div.add_children(content_div)
        return multi_div



    def parse_backside(self, back_str: str) -> list[HtmlNode]:
        
        lines = back_str.splitlines(False)
        md_str = ""
        multi_div = None
        
        if config.cardloader.collapse:
            has_choices = False
        
            for i, line in enumerate(lines):
                if MultipleChoiceCard.is_multi(line):
                    multi_div = self.parse_multi(lines, i)
                    self.not_collapse = True
                    has_choices = True
                    break
                else:
                    md_str += line
            
            if not has_choices:
                raise CardSyntaxError("Multiple choice card has no choices.")

            pre_elems = parse_markdown(md_str)
        
            return [*pre_elems, multi_div] if multi_div else pre_elems
        else:
            return [HtmlNode("div", *parse_markdown(back_str))]