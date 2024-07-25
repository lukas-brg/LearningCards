#!/bin/bash

# for file in ./examples/*.md; do
#     [ -f "$file" ] || break
#     carddown $file
# done

carddown examples/cards.md
carddown --toc --toc-lvl 3 examples/markdown_demo.md 
carddown --toc examples/read_me.md
carddown --toc --toc-lvl 3 --theme light --title "Markdown Demo Light Theme" examples/markdown_demo.md examples/markdown_demo_light_theme.html
carddown examples/escape_test.md