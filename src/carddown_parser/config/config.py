import os, sys, json, traceback
import appdirs
import toml



ENABLE_DEBUG = False
CONFIG_FILE_NAME = "config.toml"

APP_CONFIG_PATH = os.path.join(os.path.dirname(__file__), CONFIG_FILE_NAME)
USR_CONFIG_PATH = os.path.join(appdirs.user_config_dir("carddown"), CONFIG_FILE_NAME)
CFG_PATHS = [APP_CONFIG_PATH, USR_CONFIG_PATH]


with open(os.path.join(os.path.dirname(__file__), "locals.json"), encoding="utf-8") as f:
    LOCALS = json.load(f)

class Subconfig():
    
    @classmethod
    def _check_key(cls, key):
        return key in cls.__dict__

    def overwrite(self, cfg_dict: dict[str, any]):
        for key, val in cfg_dict.items():
            if self._check_key(key):
                setattr(self, key, val)
            else:
                print(f"Warning: '{self._key}.{key}' is not a valid config attribute.")


#  =================================================== Defaults ===================================================

class MdparserConfig(Subconfig):
    
    _key = "mdparser"
    table_align = "left"

    footnote_min_indent = 4
    prettyprint_inline_code = False
    prettyprint_multiline_code = False

    # Put class name of tokens you don't want to be parsed here
    ignore_inline_tokens = []

    tabsize = 4 # When using Multiline Code indented with tabs

    checkbox_disabled = True

    list_item_chars = ['-' , '+' , '*']
    ignore_empty_lines = True



class CardloaderConfig(Subconfig):
   
    _key = "cardloader"
    file_extension_warning = True
    card_separator = "hr" # Horizontal Rule after each card, can be None
    collapse = True

    # If a card longer than LENGTH_WARNING lines is detected, there will be a warning, can be None
    # output will be rendered anyway.
    length_warning = 30 

FORMATS = ["html", "pdf"]

class DocumentConfig(Subconfig):
        
    _key = "document"
    table_of_contents = True
    format = "html"
    toc_max_heading = 3
    toc_include_cards = True
    toc_max_heading_cards = 1
    toc_show_back_headings_cards = False
    prerender_latex = True
    image_max_width = "80%"
    align = "center"
    indent_html = 2
    margin = 45 # If centered each side will get a value of margin/2, if left aligned, the right side will get margin
    static_folder = "./static"
    standalone = False
    body_class = "markdown-body"
    codeblock_copy_btn=True
    _base = "base.css"
    _light = "light.css"
    _dark = "dark.css"
    overwrite_warning = False
    open_file = False
    lang = "en"
    themes = {
        "light" : [_base, _light],
        "dark"  :  [_base, _dark],
        "raw"   : [_base],
        "none"  : [],
        "pdf"   : [_base, _light, "pdf_export.css"]
    }

    default_theme = "dark"

    # Searches in static folder
    scripts = [
        "script.js"
    ]


# =============================================================================================================


class Config:
    
    __is_instantiated = False
    __config = None

    def __init__(self):

        assert not Config.__is_instantiated

        Config.__is_instantiated = True
        
        self.__subconfs: dict[str, Subconfig] = {}
        
        for SubconfType in Subconfig.__subclasses__():
            subconf_instance = SubconfType()
            self.__subconfs[SubconfType._key] = subconf_instance
            setattr(self, SubconfType._key, subconf_instance)
        
        

    @staticmethod
    def get_config():
        if not Config.__is_instantiated:
            Config.__config = Config()
        return Config.__config
    

    @staticmethod
    def config_dict_from_file(cfg_path: str):
        try:       
            with open(cfg_path, "r") as f:
                cfg_dict = toml.loads(f.read())
            return cfg_dict
        except OSError:
            print(f"Warning: config file '{cfg_path}' not found.")
        
        

    def dict_to_toml(cfg: dict[str, any], filepath: str, overwrite_warning=False):
        
        if os.path.isdir(filepath):
            name = CONFIG_FILE_NAME
            filepath = os.path.join(filepath, name)
        
        if overwrite_warning and os.path.exists(filepath):
            if input(f"File '{filepath}' already exists.\nAre you sure you want to overwrite it? <y/N> ") != "y":
                sys.exit()

        with open(filepath, "w") as f:
            f.write(toml.dumps(cfg))


    def overwrite(self, cfg_dict: dict[str, any]):
        for key, subconf in self.__subconfs.items():
            if key in cfg_dict:
                subconf.overwrite(cfg_dict[key])      



    def load_config_file(self, cfg_path: str):

        try:       
            cfg_dict = Config.config_dict_from_file(cfg_path=cfg_path)
            self.overwrite(cfg_dict)
        except:
            if ENABLE_DEBUG:
                print(traceback.format_exc())

            print(f"Warning: Something went wrong loading config '{cfg_path}'")


    @staticmethod
    def _get_attribute_dict(objs: list):
        cfg_dict = {
            obj._key : 
                {attr : getattr(obj, attr) for attr in dir(obj) if not callable(getattr(obj,attr)) and not attr.startswith("_")}
            for obj in objs
        }
        return cfg_dict


    @staticmethod
    def generate_default_config_dict():
        cfg =  Config._get_attribute_dict(Subconfig.__subclasses__())
        return cfg

    @staticmethod
    def default_to_toml(filepath, overwrite_warning=False):
        cfg = Config.generate_default_config_dict()
        Config.dict_to_toml(cfg, filepath, overwrite_warning)
      

    @staticmethod
    def config_set(arg: str):
       
        set_vals = arg.split(" ")
        
        usr_cfg = {}

        for set_val in set_vals:
            key, val = set_val.split("=", 1)
            usr_cfg[key] = val
    
        cfg = Config.config_dict_from_file(APP_CONFIG_PATH)

        for ukey, uval in usr_cfg.items():        
            found = False
            for subconf in cfg.values():
                if ukey in subconf:
                    subconf[ukey] = json.loads(uval)
                    found = True
            if not found:
                print(f"Warning: '{ukey}={uval}' is not a valid config attribute. Disregarding...")
                    
        Config.dict_to_toml(cfg, APP_CONFIG_PATH, overwrite_warning=False)


def get_config():
    return Config.get_config()


def get_locals():
    config = get_config()
    return LOCALS[config.document.lang]


def get_local(key: str) -> str:
    return get_locals()[key]



def load_configs(args):
   
    config = get_config()
    
    config.load_config_file(APP_CONFIG_PATH)

    for cfg_path in CFG_PATHS[1:]:
        if os.path.exists(cfg_path):
            config.load_config_file(cfg_path)

    if args.config:
        config.load_config_file(args.config)   
    
    if args.collapse is not None:
        config.cardloader.collapse = args.collapse

    if args.toc is not None:
        config.document.table_of_contents = args.toc

    if args.toc_lvl is not None:
        if config.document.table_of_contents:
            config.document.toc_max_heading = args.toc_lvl
        else:
            print("Warning. Table of contents is disabled, so the '--toc-lvl' parameter is disregarded.")

    if args.align:
        if args.align == "center" or args.align == "left":
            config.document.align = args.align
        else:
            print(f"Warning: Invalid aligh option '{args.align}'. Disregarding...")
    
    if args.prerender_latex is not None:
        config.document.prerender_latex = args.prerender_latex

    if args.open is not None:
        config.document.open_file = args.open
    
    if args.lang is not None:
        if args.lang not in LOCALS:
            print(f"Warning: Invalid lang option '{args.lang}'. Only {list(LOCALS.keys())} are supported.")
            print(f"         Using default language '{config.document.lang}'")
        else: 
            config.document.lang = args.lang

    if args.margin is not None:
        margin = args.margin
        if margin < 0 or margin >= 100:
            print(f"Warning: margin parameter expects a positive number in range [0...100.] (margin={args.margin} given). Disregarding...")
        else:
            config.document.margin = margin     

    if args.standalone is not None:
        config.document.standalone = args.standalone  
