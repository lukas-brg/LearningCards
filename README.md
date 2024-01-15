# Description

Carddown is a terminal-based Markdown renderer that extends the Markdown syntax to support the inclusion of learning cards.

It is able to render arbitrary markdown files that may or may not contain any learning cards and supports the entire markdown syntax as specified [here](https://www.markdownguide.org/cheat-sheet/).

An input .md file is converted into a standalone .html file, which, when opened by a web browser, displays the learning cards and renders the Markdown elements.



# Installation


This project requires **Python 3.10** or higher to be installed on your system.

Clone this repository and run this in the project top-level directory:
```
pip install .
```

After installation the application can be started from anywhere by running `carddown ...args` in the command line.

**Note:**
On Ubuntu 22.04 there have been some issues with setuptools, so you might need to update your pip for the installation to work:

```
python3 -m pip install --upgrade pip
```


# Usage

At the very least you need to provide a path to an input file:

```
carddown [input_file]
```

A corresponding HTML file is then created in the same directory as the input file and all the default parameters are applied.

<br/>

It is also possible to specify the path to the output file and its name:

```
carddown [input_file] [output_file?]
```

<br/>

Additionally there are a number of flags and parameters:

**Flags:**

-   `--cards` / `-c` --> Renders the cards only, no markdown
-   `--shuffle` / `-s` --> Render the cards only in a random order
-   `--show-answers` / `-sh` --> Answers are shown right away
-   `--open` / `-o` --> Opens the output file with default webbrowser
-   `--toc` --> Automatically generates a table of contents based on the headings


**Parameters:**

- `--lang` --> Specifies language. Currently 'de' and 'en' are supported
- `--theme` --> Choose theme out of 'light', 'dark', 'raw', 'none'
- `--align` --> Aligns the body to the 'left' or 'center'
- `--margin` --> Total margin in percent
- `--title` -->  Title of the HTML document. If this parameter is not provided, one will be generated based on the name of the input file. 

`carddown -h/--help` lists every available flag or parameter.

<br/>

## Learning Cards

The Learning cards are split into a front side and a back side. The front side contains the question, while the back side, which is not revealed until a click on a button, contains the answer.

The learning card specific syntax uses three types of tags, all of which are wrapped in `{CURLY_BRACES}`:

1. Every card starts with a start tag, that is at the end of an H1 heading, which serves as the card title.
   - The exact tag depends on the learning card type
2. The `{BACK}` tag marks the point where the back side begins.
   - If this tag is omitted, only the H1 heading makes up the front side, the rest will be on the back side
3. The end of a card is defined by using the {END} tag:
   - The `{END}` tag can be omitted for subsequent cards or when a card is at the end of file.

<br/>

### Learning Card Types

There are three basic card types:



#### Standard Card

```
# This is the card title {CARD}

This is the front side of the card. It can contain any markdown syntax

{BACK}

## The back side starts after the back tag

This text is on the back side.

{END}

```


If you don't need much text on the front side you can also use this format:


```
# Only this h1 heading will be on the front side {CARD}

The rest will appear on the back side

{END}
```

**Note:** This format where there is no `{END}` tag works for every card type.



<br/>

#### Multiple Choice Card

```
# Multiple Choice Card {MULTI}

This card contains displays multiple choices of which one or more have to be marked as correct.

{BACK}

- [x] Correct Answer 1
- [ ] Incorrect Answer
- [x] Correct Answer 2

This text will be revealed after the choice is confirmed.

{END}

```


<br/>

#### Answer Card

This card includes a textbox in which the user must input an answer.

```
# Answer Card {ANSWER}

What is 1+1?

{BACK}

1+1={2}

{END}

```

The correct answer is contained inside `{BRACKETS}`

**Note**: You can find some more practical examples in [examples/cards.md](./examples/cards.md) and look at the result by downloading [examples/cards.html](./examples/cards.html) and opening it in a web browser.

<br/>

## Configuration

Carddown uses `.toml` files for configuration and provides a second entry point called `carddown-config` to handle all things related to configuration.

A config file does not need to contain every available parameter. When using a custom config file, the parameters within it overwrite the defaults, while the remaining parameters follow the default settings.

Run `carddown-config --help` to list out every option regarding configuration.

<br/>

### Creating a User Config File

Carddown already uses an application config file located within the project directory. However, users can create their own config file.

For user convenience, a user config file containing the default settings can automatically be generated, at a location that is determined platform independently, by running the following command:

```
carddown-config --make-usr 
```

The path to the config file will be a printed to the terminal, so you can open it and edit the parameters according to your needs. The file will automatically be loaded by carddown.

<br/>

### Undoing the Configurations made

If you want to restore the defaults, you can either run 
`carddown-config --make-usr` again and chose to overwrite the existing config file to bring it back to its defaults or remove the user config file entirely by running:

```
carddown-config --rm-usr
```

<br/>

### Using a Custom Configuration to Render a Single File

When using carddown to reder a Markdown file, you can use the `--config [CONFIG_PATH]` parameter to use a custom config file and apply it just to this specific markdown file.

Example:

```
carddown --config [CONFIG_PATH] [MARKDOWN_PATH] [OUTPUT_PATH?]
```

To create such a config file easily, there is a command which can generate a default config file at any given location:

```
carddown-config --make [PATH?]
```

If no path is provided the file will be created in the current working directory.


