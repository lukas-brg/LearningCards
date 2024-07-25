
This table of contents was auto-generated. The feature can either be set in the config as default behaviour or it can be enabled for a single file by using the `--toc` flag.

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

*This is italic text*

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

## Escaping Markdown Syntax

```
This \*should\* be displayed as plain text.
```

This \*should\* be displayed as plain text.

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
3. foo
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

### Inline Code

```
Inline `code`
```

Inline `code`

### Indented code blocks



```
Every line that is indented by 4 spaces or more will be displayed as a code block. The lines of code will keep their relative indentation.

    This is a line of code
      This is another line of code

This is normal text.

```

Every line that is indented by 4 spaces or more will be displayed as a code block. The lines of code will keep their relative indentation.

    This is a line of code
      This is another line of code

This is normal text.

### Block code "fences"



```
  ```
  Sample text here...
  ```
```

```
Sample text here...
```



#### Syntax highlighting

Specify the language after the code block opening fences, 'auto' is also accepted.

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


The exact width of the columns does not need to be consistent, only the number of columns does.

```
| Column A| Column B   | Column C   |
| -------- | ------------ | ---------------- |
| 1            | 7  |   13             |
|  3        |9   |   15             |
| 5            | 11 |  17             |
```


| Column A| Column B   | Column C   |
| -------- | ------------ | ---------------- |
| 1            | 7  |   13             |
|  3        |9   |   15             |
| 5            | 11 |  17             |


## Links

```
[link text](http://dev.nodeca.com)

[link with title](http://nodeca.github.io/pica/demo/ "title text!")

Autoconverted link https://github.com/nodeca/pica 

```

[link text](http://dev.nodeca.com)

[link with title](http://nodeca.github.io/pica/demo/ "title text!")

Autoconverted link https://github.com/nodeca/pica 


### Linking to Headings

You can create links to headings within this document using the following rules:

- Remove all non-alphanumeric characters from the heading text.
- Replace single and consecutive spaces with one dash `-`.
- Convert the text to all-lowercase.

If duplicate headings exist and you want to link to them, append `-[COUNT]` to the end of the link, where `COUNT=1` refers to the first duplicate.


```
[Link to first H1 Heading](#h1-heading)

[Link to second H1 Heading](#h1-heading-1)

[Link to this section's heading](#linking-to-headings)
```


[Link to first H1 Heading](#h1-heading)

[Link to second H1 Heading](#h1-heading-1)

[Link to this section's heading](#linking-to-headings)

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




## [Emojies](https://github.com/markdown-it/markdown-it-emoji)

```
Classic markup: :wink: :crush: :cry: :tear: :laughing: :yum:
```

Classic markup: :wink: :crush: :cry: :tear: :laughing: :yum:




## Subscript / Superscript


```
- 19^th^
- H~2~O

```

- 19^th^
- H~2~O



## Footnotes


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

## Definition lists

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

### Inline Equations

```
Inline latex equation $\forall x \in X, \quad \exists y \leq \epsilon\$

Another inline equation $\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}$

```

Inline latex equation $\forall x \in X, \quad \exists y \leq \epsilon$

Another inline equation $\int_{-\infty}^{\infty} e^{-x^2} \, dx = \sqrt{\pi}$


### Block Equations

```
$$\frac{n!}{k!(n-k)!} = \binom{n}{k}$$

$$\frac{1}{2\pi i} \oint_\gamma \frac{f(z)}{z-z_0} \, dz = f(z_0) \cdot \sum_{n=0}^{\infty} \frac{1}{z_0 - a_n}$$
``` 


$$\frac{n!}{k!(n-k)!} = \binom{n}{k}$$

$$\frac{1}{2\pi i} \oint_\gamma \frac{f(z)}{z-z_0} \, dz = f(z_0) \cdot \sum_{n=0}^{\infty} \frac{1}{z_0 - a_n}$$


### Escaping Latex Syntax

If the Latex Syntax conflicts with something you want to be displayed, you can use backslashes to escape the `$`.
**Note:** Within code elements Latex equations won't be rendered anyway, so you can use the `$` character safely there.



```
\$\forall x \in X, \quad \exists y \leq \epsilon\$

\$\$\frac{1}{2\pi i} \oint_\gamma \frac{f(z)}{z-z_0} \, dz = f(z_0) \cdot \sum_{n=0}^{\infty} \frac{1}{z_0 - a_n}\$\$
```

**This should not be rendered as an equation:**

\$\forall x \in X, \quad \exists y \leq \epsilon\$

\$\$\frac{1}{2\pi i} \oint_\gamma \frac{f(z)}{z-z_0} \, dz = f(z_0) \cdot \sum_{n=0}^{\infty} \frac{1}{z_0 - a_n}\$\$


# h1 Heading

This heading's purpose is to test whether the links in the table of contents still work with duplicate headings and to demonstrate how linking to duplicate headings works.




