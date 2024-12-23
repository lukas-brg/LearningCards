import requests
import urllib


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
