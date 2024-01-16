import os, sys, argparse, traceback, re
import pdfkit
import webbrowser

from .config.config import load_configs, Config, CFG_PATHS, ENABLE_DEBUG, APP_CONFIG_PATH, USR_CONFIG_PATH
from .mdparser.htmltree import HtmlFile
from .cardloader import CardLoader
from .errors import MarkdownSyntaxError, show_exception_msg, show_warning_msg, CardSyntaxError, debug_print


config = Config.get_config()

PACKAGE_DIR = os.path.dirname(__file__)
DEBUG_DEFAULT_FILE = "examples/test2.md"

def get_static_folder():
    return os.path.join(PACKAGE_DIR, config.document.static_folder) if not os.path.isabs(config.document.static_folder) else config.document.static_folder


def get_next_filename(filepath):
    filename, file_extension = os.path.splitext(filepath)
    base_filename = filename
    count = 1
    while os.path.exists(f"{base_filename}({count}){file_extension}"):
        count += 1
    return f"{base_filename}({count}){file_extension}"

def existing_file_prompt(filepath):
    while os.path.exists(filepath):
        print(f"The file '{filepath}' already exists.")
        print("Choose an option:")
        print("1. Abort")
        print("2. Rename the file")
        print("3. Overwrite the existing file")
        print("4. Automatically rename the file (e.g., 'your_file(1).txt')")

        choice = input("Enter the number of your choice: ")

        if choice == '1':
            print("Aborting. No changes will be made.")
            return None

        elif choice == '2':
            new_filename = input("Enter the new filename: ")
            base_dir = os.path.dirname(filepath)
            filepath = os.path.join(base_dir, new_filename)

        elif choice == '3':
            confirm_overwrite = input(f"Are you sure you want to overwrite '{filepath}'? (yes/no): ")
            if confirm_overwrite.lower() == 'yes':
                print("Overwriting the existing file.")
                return filepath
            else:
                print("Operation canceled. No changes will be made.")

        elif choice == '4':
            filepath = get_next_filename(filepath)
            print(f"Automatically renaming the file to '{os.path.basename(filepath)}'.")

        else:
            print("Invalid choice. Please enter a valid option.")

    return filepath


def get_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--cards", action="store_true", help="Renders cards only, no markdown")
    parser.add_argument("-s", "--shuffle", action="store_true", help="Renders the cards in a random order")
    parser.add_argument("-sh", "--show-answers", action="store_false", dest="collapse", help="Removes the option to collapse answers", default=None)
    parser.add_argument("--hide-answers", action="store_true", dest="collapse", default=None)
    parser.add_argument("--theme", default=None, required=False, help=f"Available themes: {list(config.document.themes.keys())}")
    parser.add_argument("-t", "--title", required=False, help="Choose a document title. If ommited one is generated automatically using the file name")
    parser.add_argument("--toc", required=False, action="store_true", dest="toc", default=None, help="Automatically generates a table of contents")
    parser.add_argument("--no-toc", required=False, action="store_false", dest="toc")
    parser.add_argument("--toc-lvl", required=False, help="Specifies the maximun heading level displayed in the table of contents", type=int)
    parser.add_argument("--css", default=None, required=False, help="Include your own css file")
    parser.add_argument("--margin",  required=False, type=int)
    parser.add_argument("--export", required=False, help="Export to 'pdf or 'json'")
    parser.add_argument("--lang", required=False)

    parser.add_argument("--rec", "-r", required=False, action="store_true", default=False, help="Recursively traverses directory tree and converty any '.md' file into an '.html' file")
    
    parser.add_argument("--align", required=False)

    
    parser.add_argument("--styles", action="store_true", default=False, help="""
                        If you are exporting the cards to json this option will output the raw markdown. 
                        If this option is not present, only the text will be exported"""
    )

    parser.add_argument("--config", required=False, help="Include your own config file")
    parser.add_argument("-o", "--open", action="store_true", dest="open", help="Opens the output file in default browser", default=None)
    parser.add_argument("--no-open", action="store_false", dest="open")
  
    parser.add_argument("input_file", nargs='?') 
    parser.add_argument("output_file", nargs='?')
    
    args = parser.parse_args()

    if not ENABLE_DEBUG and not args.input_file:
        parser.error("An input file is required.")
    
    return args
    


def load_theme(theme):

    if theme not in config.document.themes:
        show_warning_msg(f"Theme '{theme}' not available, using default theme '{config.document.default_theme}'")
        styles = config.document.themes[config.document.default_theme]
    else:
        styles = config.document.themes[theme]
    
    static_folder = get_static_folder()
    return [os.path.join(static_folder, style) for style in styles]


def load_scripts():
    static_folder = get_static_folder()
    return [os.path.join(static_folder, script) for script in config.document.scripts]


def get_filepaths(args, output_file_extension):

    if not args.input_file:
        input_file = DEBUG_DEFAULT_FILE
       
    else:
        input_file = args.input_file
    # ------------------------------

    name = os.path.basename(input_file)
    directory = os.path.dirname(input_file)
    name, extension = name.rsplit(".", 1)
   
    if config.cardloader.file_extension_warning and extension != "md":
        show_warning_msg(f"File ending '.{extension}' detected. Only markdown files are supported.")
        if input("Continue? <y/N> ") != "y":
            sys.exit()
    
    # if no output path is provided, the output of filename.md is stored as filename.html in the working directory
    if not args.output_file:
        output_file = os.path.join(directory, name + "." + output_file_extension)
    else:
        output_file = args.output_file

    if os.path.isdir(output_file):
        output_file = os.path.join(output_file, name+"."+output_file_extension)

    return input_file, output_file, name


def get_title(args, name):
    if args.title:
        return args.title
    else:
        #return ' '.join(x.capitalize() or '_' for x in name.split('_'))
        return ' '.join((group.capitalize() if group[0].isalpha() else group) for group in re.findall('([a-zA-Z]+|[0-9]+)', name))


def try_parse_file(filepath: str,):
    loader = CardLoader()
    try:
        loader.parse_file(filepath)
    except CardSyntaxError as e:
        show_exception_msg(e)
        sys.exit()
    except MarkdownSyntaxError as e:
        show_exception_msg(e)
        sys.exit()
    return loader

def export(args):
    args.collapsible = False

    
    if args.export == "json":
        input_file, output_file, name = get_filepaths(args, "json")
        loader = try_parse_file(input_file)
        loader.cards.to_json(output_file, include_styles=args.styles)
    
    elif args.export == "pdf":
        config.cardloader.collapse = False
    
        input_file, output_file, name = get_filepaths(args, "pdf")
        title = get_title(args, name)
        styles = load_theme("pdf")
        
        loader = try_parse_file(loader, input_file)
        
        html = HtmlFile(styles=styles, title=title)
        if args.shuffle:
            loader.cards.shuffle()

        if args.cards:
            html.body.add_children(*loader.get_cards())
        else:
            html.body.add_children(*loader.get_cards_and_markdown())

        pdfkit.from_string(str(html), output_file)

    print(f"Sucessfully exported '{input_file}' to '{output_file}'")


def alignment_css(padding_left, padding_right):
    
    return f"""
    .{config.document.body_class} {{ 
            padding-left: {padding_left};
            padding-right: {padding_right}
    }}

    @media only screen and (orientation: portrait) {{
    .{config.document.body_class} {{
            padding: 50px;
    }}
}} 
    """



def to_html(args):
    
    input_file, output_file, name = get_filepaths(args, "html")
    
    loader = try_parse_file(input_file)
    scripts = load_scripts()
    if not args.theme:
        args.theme = config.document.default_theme
    styles = load_theme(args.theme)
    title = get_title(args, name)
    
    if css_path := args.css:
        styles.append(css_path)

    if config.document.align == "left":
       align_style = alignment_css("15px", f"{config.document.margin}%")
    else:
        align_style = alignment_css(f"{config.document.margin  / 2}%", f"{config.document.margin / 2}%")
    

    html = HtmlFile(scripts, styles, title, align_style)

    if args.cards:
        html.body.add_children(*loader.get_cards(shuffle=args.shuffle))
    else:
        html.body.add_children(*loader.get_cards_and_markdown())

    if config.document.overwrite_warning and os.path.exists(output_file):
        if input(f"Warning: file {output_file} already exists.\nAre you sure you want to overwrite it? <y/N> ") != "y":
            sys.exit()

    html.save(output_file)
    
    print(f"Sucessfully converted '{input_file}' to '{output_file}'")

    if config.document.open_file:
        if not os.path.isabs(output_file):
            output_file = os.path.realpath(output_file)
        url = "file:///" + output_file
        webbrowser.open(url)


    
def carddown_config():
    parser = argparse.ArgumentParser()
    
    parser.add_argument("--paths", required=False, action="store_true",  help="Outputs the paths the application is looking for config files")
    parser.add_argument("--set", required=False, dest="set_conf", default=None, help="Changes config values at the application level. Format: --set attr_1=value_1 attr_2=value_2 ...")
    parser.add_argument("--reset", required=False, action="store_true", help="Restores the default config values for the application level config file.")
    parser.add_argument("--make", required=False, action="store_true", help="Creates a config file at the given path or at the current working directory, if no path is specified.")
    parser.add_argument("--make-usr", required=False, action="store_true", help="Creates a user config file and outputs the location")
    parser.add_argument("--rm-usr", required=False, action="store_true", help="Removes the user config file")
    parser.add_argument("output_dir", nargs='?')
    args = parser.parse_args()
    
    if args.paths:
        print(f"Configs can be stored at:\n{CFG_PATHS}")
        print("Note: Later configs overwrite earlier ones.")

    elif args.reset:
        Config.default_to_toml(APP_CONFIG_PATH)

    elif args.set_conf:
        try:
            Config.config_set(args.set_conf)
        except ValueError:
            if ENABLE_DEBUG:
                traceback.print_exc()
            parser.error("Invalid format!")
        except:
            if ENABLE_DEBUG:
                traceback.print_exc()
            parser.error("Something went wrong!")
      

    elif args.make:
        if not args.output_dir:
            dest = os.getcwd()
        else:
            dest = args.output_dir
        Config.default_to_toml(dest, overwrite_warning=True)
    
    elif args.make_usr:
        dest = USR_CONFIG_PATH
        dir = os.path.dirname(dest)
        if not os.path.exists(dir):
            os.makedirs(dir)
        Config.default_to_toml(dest, overwrite_warning=True)
        print(f"Created user config at '{dest}'")
    
    elif args.rm_usr:
        dest = USR_CONFIG_PATH
        if not os.path.exists(dest):
            sys.exit()

        os.remove(dest)
        
    else:
        parser.error("Need to specify an option")

   

def main():
    args = get_args()
    
    if args.shuffle:
        args.cards = True

    debug_print("Started application")
    debug_print("Args:", args)
    
    load_configs(args)

    if args.export:
        export(args)
    else:
        to_html(args)
