#!/bin/bash

# for file in ./examples/*.md; do
#     [ -f "$file" ] || break
#     carddown $file
# done

carddown examples/cards.md
carddown --toc --toc-lvl 3 examples/markdown_test.md 
carddown --toc examples/read_me.md