from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from textwrap import indent
from typing import List, Optional

from nbconvert import HTMLExporter
from nbconvert.preprocessors import tagremove

from . import preprocessors, utils


@dataclass
class TOCTree:
    title: Optional[str] = None
    anchor: Optional[str] = None
    children: List["TOCTree"] = field(default_factory=list)

    def __str__(self):
        if self.children:
            return (self.title or "<root>") + "\n" + indent("\n".join(str(c) for c in self.children), " ")
        else:
            return self.title

    def to_html_list(self, url="", max_depth=1, wrap=False, depth=0) -> str:
        anchor_text = f"#{self.anchor}" if self.anchor else ""
        link_text = f'<a href="{url}{anchor_text}">{self.title}</a>' if self.anchor is not None else self.title

        if self.children and depth < max_depth:
            children = "\n".join(c.to_html_list(url, max_depth, depth=depth + 1) for c in self.children)
            if self.title:
                return f"<li>{link_text}\n <ol>\n{indent(children, '  ')}\n </ol>\n</li>"
            else:
                if wrap:
                    return f"<ol>\n{indent(children, ' ')}\n</ol>"
                else:
                    return indent(children, ' ')
        else:
            if self.title:
                return f"<li>{link_text}</li>"
            else:
                return ""


class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_header = False
        self.current_header_level = None
        self.current_header_title = None
        self.current_header_link = None
        self.headers = []

    def handle_starttag(self, tag, attrs):
        if tag in {"h1", "h2", "h3"}:
            attrs = dict(attrs)
            if attrs.get("id") in {"main-title", "Exercise", "Exercises"}:
                return
            self.in_header = True
            self.current_header_level = tag[1]
            self.current_header_link = attrs.get("id")

    def handle_endtag(self, tag):
        if tag in {"h1", "h2", "h3"} and self.in_header:
            self.headers.append({"level": int(self.current_header_level), "title":  self.current_header_title, "anchor": self.current_header_link})

            self.in_header = False
            self.current_header_level = None
            self.current_header_title = None
            self.current_header_link = None

    def handle_data(self, data):
        if self.in_header and self.current_header_title is None:
            self.current_header_title = data


def get_headers(html: str) -> TOCTree:
    """
    Given a HTML string, extract the table of contents
    """
    parser = MyHTMLParser()
    parser.feed(html)
    parser.close()

    toc = TOCTree()

    for header in parser.headers:
        temp_toc = toc
        new_toc = TOCTree(header["title"], header["anchor"])
        for _ in range(header["level"] - 1):
            try:
                temp_toc = temp_toc.children[-1]
            except IndexError:
                pass
        temp_toc.children.append(new_toc)

    if len(toc.children) == 1:
        toc.children[0].anchor = ""

    return toc


def construct_toc(chapters: List[Path], config, skip_first_page=True) -> str:
    """
    Given some ipynb filenames, return the HTML table of contents
    """
    toc = []

    plain_html_exporter = HTMLExporter(config=config)
    plain_html_exporter.register_preprocessor(tagremove.TagRemovePreprocessor, enabled=True)
    plain_html_exporter.register_preprocessor(preprocessors.PageLinks(chapters), enabled=True)

    for filename in chapters:
        body, resources = utils.ipynb_to_html(plain_html_exporter, filename)
        out_filename = resources["output_stem"] + resources["output_extension"]
        header_list = get_headers(body).to_html_list(out_filename, max_depth=1)
        toc.append(header_list)

    if skip_first_page:
        toc = toc[1:]

    inner_toc_string = '\n'.join(toc)
    full_toc_html = f"<ol>\n{inner_toc_string}\n</ol>"
    return full_toc_html
