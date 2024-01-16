#!/bin/bash

for file in ./examples/*.md; do
    [ -f "$file" ] || break
    carddown $file
done
