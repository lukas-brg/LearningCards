import requests
import urllib
import os
from abc import ABC
import traceback
from .htmltree import HtmlFile
from ..config import get_config, ENABLE_DEBUG

config = get_config()


def latex_to_svg(latex_code):
    params = {
        "formula": latex_code,
        "out": 2,
        "preamble": "\\usepackage{amsmath} \\usepackage{amsfonts} \\usepackage{amssymb}",
    }

    payload = urllib.parse.urlencode(
        params,
        quote_via=urllib.parse.quote
    )

    response = requests.post(
        "https://www.quicklatex.com/latex3.f", data=payload)

    svgurl = response.text.split("\n")[-1].split(" ")[0].replace("png", "svg")
    svgtext = requests.get(
        svgurl, headers={"Accept-Encoding": "identity"}).text

    return svgtext.replace("\n", "")


class LatexHtmlRenderer(ABC):
    includes: str
    script: str
    completion_selector: str

    @classmethod
    def attach_to_html(cls, html: HtmlFile):
        html.head_script_str += cls.script
        html.head_str += cls.includes


class KatexRenderer(LatexHtmlRenderer):

    completion_selector = ".katex"

    includes = """
    <!-- KaTeX CSS -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.15.2/dist/katex.min.css">

    <!-- KaTeX JS -->
    <script src="https://cdn.jsdelivr.net/npm/katex@0.15.2/dist/katex.min.js"></script>

    <!-- KaTeX Auto-Render JS -->
    <script src="https://cdn.jsdelivr.net/npm/katex@0.15.2/dist/contrib/auto-render.min.js"></script>
    """

    script = """
  document.addEventListener("DOMContentLoaded", function() {
    if (typeof renderMathInElement === 'function') {
        renderMathInElement(document.body, {
            delimiters: [
                { left: "$$", right: "$$", display: true },
                { left: "$", right: "$", display: false }
            ]
        });
    } else {
        console.error("KaTeX is not available.");
    }
});
    """


class MathJaxRenderer(LatexHtmlRenderer):

    completion_selector = ".MJX-TEX"

    includes = """
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
    """

    script = """
    MathJax = {
        tex: {
            inlineMath: [['$', '$']],
            displayMath: [['$$', '$$']]
        },
        svg: {
            fontCache: 'global'
        }
    };
    """


def render_latex_webdriver(html_content: str, renderer: LatexHtmlRenderer):
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC

    with open("temp.html", "w", encoding="utf-8") as f:
        f.write(html_content)
        path = os.path.realpath(f.name)

    try:
        service = Service('/usr/bin/chromedriver')
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        with webdriver.Chrome(service=service, options=options) as driver:
            driver.get("file://" + path)

            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, renderer.completion_selector))
            )

            rendered_html = driver.page_source
        return rendered_html
    except Exception as e:
        print("Warning: Something went wrong rendering LaTex via webdriver. Continuing without rendering LaTex...")
        if ENABLE_DEBUG:
            traceback.print_exc(e)
        return html_content
    finally:
        if ENABLE_DEBUG is False:
            os.remove(path)
