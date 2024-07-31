import requests, urllib


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

    response = requests.post("https://www.quicklatex.com/latex3.f", data=payload)
 
    svgurl = response.text.split("\n")[-1].split(" ")[0].replace("png", "svg")
    svgtext = requests.get(svgurl, headers={"Accept-Encoding": "identity"}).text
    
    return svgtext.replace("\n", "")


 # fig, ax = plt.subplots(figsize=(6, 1))
        # ax.text(0.5, 0.5, self.match.group(1), fontsize=20, va='center', ha='center')
        # ax.axis('off')
        # with io.StringIO() as buf:
        #     plt.savefig(buf, format='svg')
        #     svg_data = buf.getvalue()

        # print(svg_data)
        # plt.close(fig)