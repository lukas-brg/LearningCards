
import sys, os
from setuptools import setup, find_packages

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

setup(
    name="carddown",
    description="Terminal-based Markdown renderer that extends the Markdown syntax to support the inclusion of learning cards.",
    install_requires=["pdfkit", "toml", "appdirs"],
    python_requires='>=3.10',
    entry_points={
        "console_scripts" : [
            "carddown = carddown_parser:main",
            "carddown-config = carddown_parser:carddown_config"
        ]
    },
    package_dir={"" : "src"},
            
    packages=["carddown_parser", "carddown_parser.mdparser", "carddown_parser.config"],
    include_package_data=True,
    
    version="1.0.0"
)