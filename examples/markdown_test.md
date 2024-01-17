
# h1 Heading 

## h2 Heading

### h3 Heading

#### h4 Heading

##### h5 Heading

###### h6 Heading


## Horizontal Rules



---

***


## Emphasis

**This is bold text**


_This is italic text_

~~Strikethrough~~

_This text tests **nested** fontstyles_

## Blockquotes


> A blockquote starts with `>` symbol
> Blockquotes can also be nested...
>> ...by using additional greater-than signs right next to each other...



## Lists

**Unordered**

+ Create a list by starting a line with `+`, `-`, or `*`
+ Sub-lists are made by indenting 2 spaces:
  - Marker character change forces new list start:
    * Ac tristique libero volutpat at
    + Facilisis in pretium nisl aliquet
    - Nulla volutpat aliquam velit
+ Very easy!

**Ordered**

1. Lorem ipsum dolor sit amet
2. Consectetur adipiscing elit
3. Integer molestie lorem at massa


1. You can use sequential numbers...
1. ...or keep all the numbers as `1.`

Start numbering with offset:

57. foo
    2. baz
    1. test
1. bar

**Unordered and ordered lists can also be mixed:**

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
Sample text here...
```

Syntax highlighting

```js
var foo = function (bar) {
  return bar++;
};

console.log(foo(5));
```

## Tables

Default aligned columns

| Option | Description |
| ------ | ----------- |
| data   | path to data files to supply the data that will be passed into templates. |
| engine | engine to be used for processing templates. Handlebars is the default. |
| ext    | extension to be used for dest files. |

Right aligned columns

| Option | Description |
| ------:| -----------:|
| data   | path to data files to supply the data that will be passed into templates. |
| engine | engine to be used for processing templates. Handlebars is the default. |
| ext    | extension to be used for dest files. |

Left aligned columns

| Option | Description |
| :----- | :---------- |
| data   | path to data files to supply the data that will be passed into templates. |
| engine | engine to be used for processing templates. Handlebars is the default. |
| ext    | extension to

Center aligned columns

| Option | Description |
| :-----:| :----------:|
| data   | path to data files to supply the data that will be passed into templates. |
| engine | engine to be used for processing templates. Handlebars is the default. |
| ext    | extension to


Mixed alignments

| Left   Alignment  | Center Alignment   | Right Alignment |
| :---------------- | :------: | ----: |
| Python Hat        |   True   | 23.99 |
| SQL Hat           |   True   | 23.99 |
| Codecademy Tee    |  False   | 19.99 |
| Codecademy Hoodie |  False   | 42.99 |

## Links

[link text](http://dev.nodeca.com)

[link with title](http://nodeca.github.io/pica/demo/ "title text!")

Autoconverted link https://github.com/nodeca/pica 


## Images

![Minion](https://octodex.github.com/images/minion.png)
![Stormtroopocat](https://octodex.github.com/images/stormtroopocat.jpg "The Stormtroopocat")

Like links, Images also have a footnote style syntax

`![Alt text][id]`



## Plugins

The killer feature of `markdown-it` is very effective support of
[syntax plugins](https://www.npmjs.org/browse/keyword/markdown-it-plugin).


### [Emojies](https://github.com/markdown-it/markdown-it-emoji)

Classic markup: :wink: :crush: :cry: :tear: :laughing: :yum:




### Subscript / Superscript

- 19^th^
- H~2~O



### Footnotes

Footnote 1 link[^first].

Footnote 2 link[^second].



[^first]: Footnote **can have markup**

    and multiple paragraphs.

[^second]: Footnote text.


### Definition lists


First Term
: This is the definition of the first term.

Second Term
: This is one definition of the second term.
: This is another definition of the second term.


### Custom IDs


#### Headings can have a custom ID {#custom_id}

The custom ID can be used to [Link](#custom_id) to the heading.

## Task lists

- [x] This list item is checked
- [ ] This list item is unchecked 
  - [x] Task lists can also be nested

### Latex Equations

$$F(x) = \int^a_b \frac{1}{3}x^3$$

$$\frac{n!}{k!(n-k)!} = \binom{n}{k}$$