# A card must begin with an h1 heading and the start tag {CARD}

This is the front side of the card

{BACK}

## The backside begins after the back tag

This text is on the back side.



# Only this heading is displayed on the front side {CARD}

The rest appears on the back side


# Both the _front_ and the **back** of the card can use the whole markdown syntax {CARD}

_Here_ is some _**example**_ text to test **multiple** fontstyles in _one_ line.

{BACK}

1. list
2. list 2
3. list 3

```js
let i = 0;
```

|  a | b  | c  | d  | e  |
|----|----|----|----|----|
| 1  | 2  | 3  | 4  | 5  |
| 6  | 7  | 8  | 9  | 10 |
| 11 | 12 | 13 | 14 | 15 |


# What is 1+1? {CARD}

1+1=2

# Card Heading {CARD}

What is 1+1?

{BACK}

# This is the answer:

1+1=2


# What is 1+1? {ANSWER}

1+1={2}



# What is 1+1? {MULTI}

- [ ] 1
- [x] 2
- [ ] 3



# What is 1+1? {MULTI}

- [ ] 1
- [x] 2
- [ ] 3


# What is the capital city of Germany? {ANSWER}

Berlin


# What is a famous quote by Mahatma Gandhi? {CARD}

> You must be the change you wish to see in the world.


{END}



# Regular Markdown


1. Ordered list 1
    - unordered sublist1
    - unordered sublist2
        1. ordered subsublist1
        2. ordered subsublist2
        - unordered subsublist1
        - unordered subsublist2
    - unordered sublist 3
        - unordered subsublist1
        - unordered subsublist2
2. ordered list 2
3. ordered list 3
    1. ordered sublist1
    2. odered sublist2

-   unordered list 1
-   unordered list 2


_Here_ is some _**example**_ text to test **multiple** fontstyles in _one_ line