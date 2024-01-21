

**Note:** This file was copied from https://markdown-it.github.io/, and has been modified to adequately demonstrate the markdown syntax supported by this software.

```
# h1 Heading 

## h2 Heading

### h3 Heading

#### h4 Heading

##### h5 Heading

###### h6 Heading

```


# h1 Heading 

## h2 Heading

### h3 Heading

#### h4 Heading

##### h5 Heading

###### h6 Heading


## Horizontal Rules


```
---

***
```

---

***


## Fontstyles

```
**This is bold text**

__This is bold text__

==This is marked text==

_This is italic text_

~~Strikethrough~~

_This text tests **nested** fontstyles_
```

**This is bold text**

__This is bold text__

==This is marked text==

_This is italic text_

*This is italic text*

~~Strikethrough~~

_This text tests **nested** fontstyles_

## Blockquotes

```
> A blockquote starts with `>` symbol
> Blockquotes can also be nested...
>> ...by using additional greater-than signs right next to each other...
```

> A blockquote starts with `>` symbol
> Blockquotes can also be nested...
>> ...by using additional greater-than signs right next to each other...



## Lists

**Unordered**

```
+ Create a list by starting a line with `+`, `-`, or `*`
+ Sub-lists are made by indenting 2 spaces:
  - Marker character change forces new list start:
    * Ac tristique libero volutpat at
    + Facilisis in pretium nisl aliquet
    - Nulla volutpat aliquam velit
+ Very easy!

```

+ Create a list by starting a line with `+`, `-`, or `*`
+ Sub-lists are made by indenting 2 spaces:
  - Marker character change forces new list start:
    * Ac tristique libero volutpat at
    + Facilisis in pretium nisl aliquet
    - Nulla volutpat aliquam velit
+ Very easy!

**Ordered**

```
1. Lorem ipsum dolor sit amet
2. Consectetur adipiscing elit
3. Integer molestie lorem at massa


1. You can use sequential numbers...
1. ...or keep all the numbers as `1.`
```
1. Lorem ipsum dolor sit amet
2. Consectetur adipiscing elit
3. Integer molestie lorem at massa


1. You can use sequential numbers...
1. ...or keep all the numbers as `1.`

Start numbering with offset:

```
3.  foo
    1. baz
    2. test
1. bar

```


3.  foo
    1. baz
    2. test
1. bar

**Unordered and ordered lists can also be mixed:**

```
+ Create a list by starting a line with `+`, `-`, or `*`
+ Sub-lists are made by indenting 2 spaces:
  - Marker character change forces new list start:
    1. Lorem ipsum dolor sit amet
    2. Consectetur adipiscing elit
    3. Integer molestie lorem at massa
+ Very easy!
```

+ Create a list by starting a line with `+`, `-`, or `*`
+ Sub-lists are made by indenting 2 spaces:
  - Marker character change forces new list start:
    1. Lorem ipsum dolor sit amet
    2. Consectetur adipiscing elit
    3. Integer molestie lorem at massa
+ Very easy!


## Code

Inline `code`



Block code "fences"

```
  ```
  Sample text here...
  ```
```

```
Sample text here...
```

Syntax highlighting

```
  ```js
  var foo = function (bar) {
    return bar++;
  };
  ```
```

```js
var foo = function (bar) {
  return bar++;
};

console.log(foo(5));
```

## Tables

```
| Default Alignment| Left Alignment    | Center Alignment   | Right Alignment |
| ---------------- | :---------------- | :----------------: | --------------: |
| False            | Python Hat        |   True             | 23.99           |
| True             | SQL Hat           |   True             | 23.99           |
| True             | Codecademy Tee    |  False             | 19.99           |
| False            | Codecademy Hoodie |  False             | 42.99           |
```

| Default Alignment| Left Alignment    | Center Alignment   | Right Alignment |
| ---------------- | :---------------- | :----------------: | --------------: |
| False            | Python Hat        |   True             | 23.99           |
| True             | SQL Hat           |   True             | 23.99           |
| True             | Codecademy Tee    |  False             | 19.99           |
| False            | Codecademy Hoodie |  False             | 42.99           |

## Links

```
[link text](http://dev.nodeca.com)

[link with title](http://nodeca.github.io/pica/demo/ "title text!")

Autoconverted link https://github.com/nodeca/pica 

```

[link text](http://dev.nodeca.com)

[link with title](http://nodeca.github.io/pica/demo/ "title text!")

Autoconverted link https://github.com/nodeca/pica 


### Linking to headings

You can also link to headings of this document. For this to work all the alphanumeric characters that make up the heading text need to be present in the link. The links are also not case sensitive.

```
[Link to first H1 Heading](#h1heading)

[Another link to first H1 Heading](#h1-heading)
```

[Link to first H1 Heading](#h1heading)

[Another link to first H1 Heading](#h1-heading)

### Custom IDs

```
#### Headings can have a custom ID {#custom_id}

The custom ID can be used to [Link](#custom_id) to the heading.

```

#### Headings can have a custom ID {#custom_id}

The custom ID can be used to [Link](#custom_id) to the heading.






## Images

```
![Minion](https://octodex.github.com/images/minion.png)
![Stormtroopocat](https://octodex.github.com/images/stormtroopocat.jpg "The Stormtroopocat")
```

![Minion](https://octodex.github.com/images/minion.png)
![Stormtroopocat](https://octodex.github.com/images/stormtroopocat.jpg "The Stormtroopocat")





## Plugins

The killer feature of `markdown-it` is very effective support of
[syntax plugins](https://www.npmjs.org/browse/keyword/markdown-it-plugin).


### [Emojies](https://github.com/markdown-it/markdown-it-emoji)

```
Classic markup: :wink: :crush: :cry: :tear: :laughing: :yum:
```

Classic markup: :wink: :crush: :cry: :tear: :laughing: :yum:




### Subscript / Superscript


```
- 19^th^
- H~2~O

```

- 19^th^
- H~2~O



### Footnotes


```
Footnote 1 link[^first].

Footnote 2 link[^second].

```

Footnote 1 link[^first].

Footnote 2 link[^second].


The corresponding footnotes look like this:

```

[^first]: Footnotes _can have markup_

    and multiple paragraphs.

[^second]: Footnote text.

```


[^first]: Footnotes _can have markup_

    and multiple paragraphs.

[^second]: Footnote text.

```
Footnotes are enumerated by their order in the document, regardless of their text[^1].

[^1]: The footnotes can be split up across the document
    Though they are always displayed at the bottom

```

Footnotes are enumerated by their order in the document, regardless of their text[^1].

[^1]: The footnotes can be split up across the document
    Though they are always displayed at the bottom

### Definition lists

```
First Term
: This is the definition of the first term.

Second Term
: This is one definition of the second term.
: This is another definition of the second term.
```

First Term
: This is the definition of the first term.

Second Term
: This is one definition of the second term.
: This is another definition of the second term.

## Task lists

```
- [x] This list item is checked
- [ ] This list item is unchecked 
  - [x] Task lists can also be nested

```

- [x] This list item is checked
- [ ] This list item is unchecked 
  - [x] Task lists can also be nested

## Latex Equations

```
Inline latex equations \(forall x \in X, \quad \exists y \leq \epsilon\)
```

Inline latex equations \(\forall x \in X, \quad \exists y \leq \epsilon\)


```
$$\int^b_a \frac{1}{3}x^3$$

$$\frac{n!}{k!(n-k)!} = \binom{n}{k}$$
```

$$\int^b_a \frac{1}{3}x^3$$

$$\frac{n!}{k!(n-k)!} = \binom{n}{k}$$

# H1 Heading

This heading's purpose is to test whether the links in the table of contents still work with duplicate headings. Links to "H1 Heading" will only link to the first one, however.
If you want to link to this specific heading, you need to use a custom id.