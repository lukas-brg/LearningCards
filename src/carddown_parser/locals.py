from .config import get_config

locals = {
    "de" : {
        "show_backside" : "R&uuml;ckseite einblenden",
        "hide_backside" : "R&uuml;ckseite ausblenden",
        "check_answer" : "Pr&uuml;fen",
        "toc" : "Inhalte",
        "card" : "Karte"
    },
    
    "en": {
        
        "show_backside" : "Show Backside",
        "hide_backside" : "Hide Backside",
        "check_answer" : "Check Answer",
        "toc" : "Contents",
        "card" : "Card"
    }

}


def get_locals():
    config = get_config()
    return locals[config.document.lang]

def get_local(key: str) -> str:
    return get_locals()[key]